import React, { useEffect, useMemo, useState } from "react";
import PlayCircleOutlineOutlinedIcon from "@mui/icons-material/PlayCircleOutlineOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import SettingsIcon from "@mui/icons-material/Settings";
import { Stack } from "@mui/system";
import { GET_ML_MODELS } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import { ML_MODELS_FILTERS_NAMES } from "components/Filters/constants";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import MlModelsTable from "components/MlModelsTable";
import PageContentWrapper from "components/PageContentWrapper";
import { ProfilingIntegrationModal } from "components/SideModalManager/SideModals";
import TableLoader from "components/TableLoader";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useRefetchApis } from "hooks/useRefetchApis";
import { ML_MODELS_PARAMETERS, ML_EXECUTORS } from "urls";
import {
  GOALS_BE_FILTER,
  GOAL_STATUS,
  OWNER_BE_FILTER,
  STATUS_BE_FILTER,
  GOALS_FILTER,
  OWNER_ID_FILTER,
  EMPTY_UUID
} from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";
import { isEmpty as isEmptyObject } from "utils/objects";

const PageActionBar = () => {
  const openSideModal = useOpenSideModal();

  const refetch = useRefetchApis();

  const actionBarDefinition = {
    title: {
      messageId: "models",
      dataTestId: "lbl_ml_models"
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_MODELS])
      },
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
        link: ML_MODELS_PARAMETERS
      },
      {
        key: "btn-executors",
        icon: <PlayCircleOutlineOutlinedIcon fontSize="small" />,
        messageId: "executors",
        dataTestId: "btn_executors",
        type: "button",
        link: ML_EXECUTORS
      }
    ]
  };

  return <ActionBar data={actionBarDefinition} />;
};

const getFilterValues = ({ models }) => {
  const owners = [
    ...new Map(
      models.map(({ owner }) => {
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
      models.map(({ status }) => [
        status,
        {
          name: status
        }
      ])
    ).values()
  ];

  const goals = [
    {
      name: GOAL_STATUS.MET,
      value: true
    },
    {
      name: GOAL_STATUS.NOT_MET,
      value: false
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

const MlModels = ({ models, isLoading }) => {
  const [selectedFilters, setSelectedFilters] = useState(() => getRequestParams());

  useEffect(() => {
    updateQueryParams(selectedFilters);
  }, [selectedFilters]);

  const filteredData = useMemo(() => {
    const filters = Object.entries(selectedFilters).filter(([, filterValue]) => filterValue !== undefined);

    if (filters.length === 0) return models;

    return models.filter((model) =>
      filters.every((filter) => {
        const [filterType, filterValue] = filter;

        if (filterType === GOALS_FILTER) {
          if (!model.last_run_reached_goals || isEmptyObject(model.last_run_reached_goals)) {
            return false;
          }
          return Object.values(model.last_run_reached_goals).every(({ reached }) => reached) === filterValue;
        }

        if (filterType === OWNER_ID_FILTER) {
          if (filterValue === EMPTY_UUID) {
            return isEmptyObject(model.owner);
          }
          return model.owner.id === filterValue;
        }

        if (filterType === STATUS_BE_FILTER) {
          return model.status === filterValue;
        }

        return false;
      })
    );
  }, [models, selectedFilters]);

  const onFilterChange = (newFilters) => setSelectedFilters(newFilters);

  const filterValues = getFilterValues({ models });

  return (
    <>
      <PageActionBar />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            {isLoading ? (
              <TableLoader columnsCounter={4} showHeader />
            ) : (
              <MlModelsTable
                models={filteredData}
                appliedFilters={selectedFilters}
                filterValues={filterValues}
                onFilterChange={onFilterChange}
              />
            )}
          </div>
          <div>
            <InlineSeverityAlert messageId="mlModelsDescription" />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default MlModels;
