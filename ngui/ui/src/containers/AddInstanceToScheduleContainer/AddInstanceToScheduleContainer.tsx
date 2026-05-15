import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import {
  INSTANCE_REGULAR,
  RDS_INSTANCE_REGULAR,
} from "components/Filters/ResourceTypeFilter/ResourceTypeFilter";
import AddInstancesToScheduleForm from "components/forms/AddInstancesToScheduleForm";
import { FIELD_NAMES } from "components/forms/AddInstancesToScheduleForm/constants";
import { FormValues, TagEntry } from "components/forms/AddInstancesToScheduleForm/types";
import { getDefaultValue } from "components/forms/AddInstancesToScheduleForm/utils";
import AvailableFiltersService from "services/AvailableFiltersService";
import CleanExpensesService from "services/CleanExpensesService";
import PowerScheduleService, { type PowerScheduleResponse } from "services/PowerScheduleService";
import { isEmptyArray } from "utils/arrays";
import {
  ACTIVE_FILTER,
  CLOUD_ACCOUNT_ID_FILTER,
  END_DATE_FILTER,
  RESOURCE_TYPE_FILTER,
  START_DATE_FILTER,
} from "utils/constants";
import { getXDaysAgoRange } from "utils/datetime";

type AddInstanceToScheduleContainerProps = {
  powerScheduleId: string;
  powerSchedule?: PowerScheduleResponse;
  handleClose: () => void;
};

const INSTANCES_COUNT_LIMIT = 5000;
const REFRESH_INTERVAL_MS = 30_000;

const useGetInstances = (range, selectedDataSourceIds, appliedFilters) => {
  const { start, end } = range;

  const { useGetOnDemand } = CleanExpensesService();
  const { getData, isLoading, data } = useGetOnDemand();

  const fetchRef = useRef<() => void>(() => {});

  useEffect(() => {
    if (!isEmptyArray(selectedDataSourceIds)) {
      const fetch = () =>
        getData({
          [START_DATE_FILTER]: start,
          [END_DATE_FILTER]: end,
          [CLOUD_ACCOUNT_ID_FILTER]: selectedDataSourceIds,
          [ACTIVE_FILTER]: true,
          [RESOURCE_TYPE_FILTER]: [
            INSTANCE_REGULAR,
            RDS_INSTANCE_REGULAR,
          ],
          limit: INSTANCES_COUNT_LIMIT,
          ...appliedFilters,
        });
      fetchRef.current = fetch;
      fetch();
    }
  }, [getData, start, end, appliedFilters, selectedDataSourceIds]);

  useEffect(() => {
    const id = setInterval(() => fetchRef.current(), REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  return {
    instances: data.clean_expenses ?? [],
    isLoading,
  };
};

const useGetAvailableFilter = (range: { start: number; end: number }) => {
  const { start, end } = range;

  const { useGet: useGetFilters } = AvailableFiltersService();
  const params = useMemo(
    () => ({
      [START_DATE_FILTER]: start,
      [END_DATE_FILTER]: end,
    }),
    [end, start]
  );
  const { isLoading, filters } = useGetFilters(params);

  return {
    isLoading,
    filters,
  };
};

const AddInstanceToScheduleContainer = ({
  powerScheduleId,
  powerSchedule,
  handleClose,
}: AddInstanceToScheduleContainerProps) => {
  const { useAttachInstancesToSchedule, useUpdate, useGetResourcesLiveState } = PowerScheduleService();

  const { onAttach, isLoading: isAttachLoading } = useAttachInstancesToSchedule();
  const { onUpdate, isLoading: isUpdateLoading } = useUpdate();
  const { onGetLiveState } = useGetResourcesLiveState();

  const range = getXDaysAgoRange(true, 7);

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValue(),
  });

  const { handleSubmit, watch, getValues, setValue } = methods;

  const existingTagSelector = powerSchedule && "tag_selector" in powerSchedule ? powerSchedule.tag_selector : undefined;

  useEffect(() => {
    if (existingTagSelector?.tags) {
      const entries = Object.entries(existingTagSelector.tags).map(([key, value]) => ({ key, value }));
      setValue(FIELD_NAMES.TAG_ENTRIES, entries.length ? entries : [{ key: "", value: "" }]);
      const resourceTypes = existingTagSelector.resource_types ?? ["Instance", "RDS Instance"];
      setValue(FIELD_NAMES.TAG_INCLUDE_EC2, resourceTypes.includes("Instance"));
      setValue(FIELD_NAMES.TAG_INCLUDE_RDS, resourceTypes.includes("RDS Instance"));
    }
  }, [existingTagSelector, setValue]);

  const filters = watch(FIELD_NAMES.FILTERS);

  const selectedDataSourceIds = watch(FIELD_NAMES.DATA_SOURCES);

  const { instances, isLoading: isGetInstancesLoading } = useGetInstances(range, selectedDataSourceIds, filters);

  const { isLoading: isGetFilterValuesLoading, filters: filterValues } = useGetAvailableFilter(range);

  // Live state enrichment: override stale MongoDB stopped_allocated with AWS real-time data
  const [liveStateMap, setLiveStateMap] = useState<Record<string, string | boolean>>({});
  const instancesRef = useRef(instances);
  instancesRef.current = instances;

  const refreshLiveState = useCallback(() => {
    const current = instancesRef.current;
    if (isEmptyArray(current)) return;
    const resources = current
      .filter((inst) => inst.cloud_resource_id && inst.cloud_account_id && inst.region)
      .map((inst) => ({
        cloud_resource_id: inst.cloud_resource_id as string,
        cloud_account_id: inst.cloud_account_id as string,
        region: inst.region as string,
        resource_type: (inst.resource_type as string) ?? "Instance",
      }));
    if (!resources.length) return;
    onGetLiveState(resources).then((stateData) => {
      if (Object.keys(stateData).length) setLiveStateMap(stateData);
    });
  }, [onGetLiveState]);

  useEffect(() => {
    refreshLiveState();
  }, [instances, refreshLiveState]);

  useEffect(() => {
    const id = setInterval(refreshLiveState, REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [refreshLiveState]);

  const enrichedInstances = useMemo(
    () =>
      instances.map((inst) => {
        const liveState = liveStateMap[inst.cloud_resource_id as string];
        if (liveState === undefined) return inst;
        return { ...inst, meta: { ...(inst.meta ?? {}), stopped_allocated: liveState } };
      }),
    [instances, liveStateMap]
  );

  const onSubmit = (formData: FormValues) => {
    const instancesToAttach = Object.keys(formData.instances).filter((k) => formData.instances[k]);
    onAttach(powerScheduleId, instancesToAttach).then(() => handleClose());
  };

  const onSubmitByTags = () => {
    const formData = getValues();
    const validTags = (formData[FIELD_NAMES.TAG_ENTRIES] ?? []).filter(
      (t: TagEntry) => t.key.trim() && t.value.trim()
    );
    if (!validTags.length) return;
    const resourceTypes = [
      ...(formData[FIELD_NAMES.TAG_INCLUDE_EC2] ? ["Instance"] : []),
      ...(formData[FIELD_NAMES.TAG_INCLUDE_RDS] ? ["RDS Instance"] : []),
    ];
    if (!resourceTypes.length) return;
    const tagSelector = {
      tags: Object.fromEntries(validTags.map(({ key, value }: TagEntry) => [key.trim(), value.trim()])),
      resource_types: resourceTypes,
    };
    onUpdate(powerScheduleId, { tag_selector: tagSelector }).then(() => handleClose());
  };

  const onRemoveTagFilter = () => {
    onUpdate(powerScheduleId, { tag_selector: null }).then(() => handleClose());
  };

  return (
    <FormProvider {...methods}>
      <AddInstancesToScheduleForm
        onSubmit={handleSubmit(onSubmit)}
        onSubmitByTags={onSubmitByTags}
        onRemoveTagFilter={onRemoveTagFilter}
        instances={isEmptyArray(selectedDataSourceIds) ? [] : enrichedInstances}
        instancesCountLimit={INSTANCES_COUNT_LIMIT}
        onCancel={handleClose}
        filterValues={filterValues}
        existingTagSelector={existingTagSelector}
        isLoadingProps={{
          isSubmitLoading: isAttachLoading,
          isUpdateLoading,
          isGetInstancesLoading,
          isGetFilterValuesLoading,
        }}
      />
    </FormProvider>
  );
};

export default AddInstanceToScheduleContainer;
