import { useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { INSTANCE_REGULAR } from "components/Filters/ResourceTypeFilter/ResourceTypeFilter";
import AddInstancesToScheduleForm from "components/forms/AddInstancesToScheduleForm";
import { FIELD_NAMES } from "components/forms/AddInstancesToScheduleForm/constants";
import { FormValues } from "components/forms/AddInstancesToScheduleForm/types";
import { getDefaultValue } from "components/forms/AddInstancesToScheduleForm/utils";
import AvailableFiltersService from "services/AvailableFiltersService";
import CleanExpensesService from "services/CleanExpensesService";
import PowerScheduleService from "services/PowerScheduleService";
import { isEmpty as isEmptyArray } from "utils/arrays";
import {
  ACTIVE_FILTER,
  CLOUD_ACCOUNT_ID_FILTER,
  END_DATE_FILTER,
  RESOURCE_TYPE_FILTER,
  START_DATE_FILTER
} from "utils/constants";
import { getXDaysAgoRange } from "utils/datetime";

const INSTANCES_COUNT_LIMIT = 5000;

const useGetInstances = (range, selectedDataSourceIds, appliedFilters) => {
  const { start, end } = range;

  const { useGetOnDemand } = CleanExpensesService();
  const { getData, isLoading, data } = useGetOnDemand();

  useEffect(() => {
    if (!isEmptyArray(selectedDataSourceIds)) {
      getData({
        [START_DATE_FILTER]: start,
        [END_DATE_FILTER]: end,
        [CLOUD_ACCOUNT_ID_FILTER]: selectedDataSourceIds,
        [ACTIVE_FILTER]: true,
        [RESOURCE_TYPE_FILTER]: INSTANCE_REGULAR,
        limit: INSTANCES_COUNT_LIMIT,
        ...appliedFilters
      });
    }
  }, [getData, start, end, appliedFilters, selectedDataSourceIds]);

  return {
    instances: data.clean_expenses ?? [],
    isLoading
  };
};

const useGetAvailableFilter = (range) => {
  const { start, end } = range;

  const { useGet: useGetFilters } = AvailableFiltersService();
  const params = useMemo(
    () => ({
      [START_DATE_FILTER]: start,
      [END_DATE_FILTER]: end
    }),
    [end, start]
  );
  const { isLoading, filters } = useGetFilters(params);

  return {
    isLoading,
    filters
  };
};

const AddInstanceToScheduleContainer = ({ powerScheduleId, handleClose }) => {
  const { useAttachInstancesToSchedule } = PowerScheduleService();

  const { onAttach, isLoading: isAttachLoading } = useAttachInstancesToSchedule();

  const range = getXDaysAgoRange(true, 1);

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValue()
  });

  const { handleSubmit, watch } = methods;

  const filters = watch(FIELD_NAMES.FILTERS);

  const selectedDataSourceIds = watch(FIELD_NAMES.DATA_SOURCES);

  const { instances, isLoading: isGetInstancesLoading } = useGetInstances(range, selectedDataSourceIds, filters);

  const { isLoading: isGetFilterValuesLoading, filters: filterValues } = useGetAvailableFilter(range);

  const onSubmit = (formData: FormValues) => {
    const instancesToAttach = Object.keys(formData.instances);
    onAttach(powerScheduleId, instancesToAttach).then(() => handleClose());
  };

  return (
    <FormProvider {...methods}>
      <AddInstancesToScheduleForm
        onSubmit={handleSubmit(onSubmit)}
        instances={isEmptyArray(selectedDataSourceIds) ? [] : instances}
        instancesCountLimit={INSTANCES_COUNT_LIMIT}
        onCancel={handleClose}
        filterValues={filterValues}
        isLoadingProps={{
          isSubmitLoading: isAttachLoading,
          isGetInstancesLoading,
          isGetFilterValuesLoading
        }}
      />
    </FormProvider>
  );
};

export default AddInstanceToScheduleContainer;
