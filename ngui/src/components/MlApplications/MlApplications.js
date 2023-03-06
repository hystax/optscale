import React, { useEffect, useMemo, useState } from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import ActionBar from "components/ActionBar";
import { ML_MODELS_FILTERS_NAMES } from "components/Filters/constants";
import { checkGoalsFilter } from "components/Filters/GoalsFilter/GoalsFilter";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import MlApplicationsTable from "components/MlApplicationsTable";
import PageContentWrapper from "components/PageContentWrapper";
import { ProfilingIntegrationModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { ML_APPLICATIONS_PARAMETERS } from "urls";
import {
  GOALS_BE_FILTER,
  GOAL_STATUS,
  OWNER_BE_FILTER,
  STATUS_BE_FILTER,
  GOALS_FILTER,
  OWNER_ID_FILTER,
  EMPTY_UUID
} from "utils/constants";
import { getQueryParams, updateQueryParams } from "utils/network";
import { isEmpty as isEmptyObject } from "utils/objects";

const PageActionBar = () => {
  const openSideModal = useOpenSideModal();

  const actionBarDefinition = {
    title: {
      messageId: "applicationsTitle",
      dataTestId: "lbl_ml_applications"
    },
    items: [
      {
        key: "btn-profiling-integration",
        icon: <SettingsIcon fontSize="small" />,
        messageId: "profilingIntegration",
        dataTestId: "btn_profiling_integration",
        type: "button",
        action: () => openSideModal(ProfilingIntegrationModal, {})
      },
      {
        key: "btn-manage-parameters",
        icon: <SettingsIcon fontSize="small" />,
        messageId: "manageParameters",
        dataTestId: "btn_manage_parameters",
        type: "button",
        link: ML_APPLICATIONS_PARAMETERS
      }
    ]
  };

  return <ActionBar data={actionBarDefinition} />;
};

const getFilterValues = ({ applications }) => {
  const owners = [
    ...new Map(
      applications.map(({ owner }) => {
        if (isEmptyObject(owner)) {
          return [null, null];
        }

        const { id, name } = owner;

        return [
          id,
          {
            id,
            name
          }
        ];
      })
    ).values()
  ];

  const statuses = [
    ...new Map(
      applications.map(({ status }) => [
        status,
        {
          name: status
        }
      ])
    ).values()
  ];

  const goals = [
    {
      name: GOAL_STATUS.MET
    },
    {
      name: GOAL_STATUS.NOT_MET
    }
  ];

  return {
    [OWNER_BE_FILTER]: owners,
    [STATUS_BE_FILTER]: statuses,
    [GOALS_BE_FILTER]: goals
  };
};

const getRequestParams = () => {
  const queryParams = getQueryParams();

  const getFiltersRequestParams = () =>
    ML_MODELS_FILTERS_NAMES.reduce(
      (params, queryKey) => ({
        ...params,
        [queryKey]: queryParams[queryKey]
      }),
      {}
    );
  return getFiltersRequestParams();
};

const MlApplications = ({ applications, isLoading }) => {
  const [selectedFilters, setSelectedFilters] = useState(() => getRequestParams());

  useEffect(() => {
    updateQueryParams(selectedFilters);
  }, [selectedFilters]);

  const filteredData = useMemo(() => {
    const filters = Object.entries(selectedFilters).filter(([, filterValue]) => filterValue !== undefined);

    if (filters.length === 0) return applications;

    return applications.filter((item) =>
      filters.every((filter) => {
        const [filterType, filterValue] = filter;

        if (filterType === GOALS_FILTER) {
          if (item.run_goals.length === 0) {
            return false;
          }
          return checkGoalsFilter[filterValue](
            item.run_goals.map(({ tendency, target_value: targetValue, last_run_value: value }) => ({
              tendency,
              targetValue,
              value
            }))
          );
        }

        if (filterType === OWNER_ID_FILTER) {
          if (filterValue === EMPTY_UUID) {
            return isEmptyObject(item.owner);
          }
          return item.owner.id === filterValue;
        }

        if (filterType === STATUS_BE_FILTER) {
          return item.status === filterValue;
        }

        return false;
      })
    );
  }, [applications, selectedFilters]);

  const onFilterChange = (newFilters) => setSelectedFilters(newFilters);

  const filterValues = getFilterValues({ applications });

  return (
    <>
      <PageActionBar />
      <PageContentWrapper>
        <MlApplicationsTable
          data={filteredData}
          appliedFilters={selectedFilters}
          filterValues={filterValues}
          onFilterChange={onFilterChange}
          isLoading={isLoading}
        />
        <InlineSeverityAlert messageId="mlApplicationsDescription" />
      </PageContentWrapper>
    </>
  );
};

export default MlApplications;
