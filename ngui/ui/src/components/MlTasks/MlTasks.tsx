import { useEffect, useMemo, useState } from "react";
import PlayCircleOutlineOutlinedIcon from "@mui/icons-material/PlayCircleOutlineOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import SettingsIcon from "@mui/icons-material/Settings";
import { Stack } from "@mui/system";
import { GET_ML_TASKS } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import { ML_TASKS_FILTERS_NAMES } from "components/Filters/constants";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import MlTasksTable from "components/MlTasksTable";
import PageContentWrapper from "components/PageContentWrapper";
import { ProfilingIntegrationModal } from "components/SideModalManager/SideModals";
import TableLoader from "components/TableLoader";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useRefetchApis } from "hooks/useRefetchApis";
import { ML_TASK_METRICS, ML_EXECUTORS } from "urls";
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
      messageId: "tasks",
      dataTestId: "lbl_ml_tasks"
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_TASKS])
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
        key: "btn-manage-metrics",
        icon: <SettingsIcon fontSize="small" />,
        messageId: "manageMetrics",
        dataTestId: "btn_manage_metrics",
        type: "button",
        link: ML_TASK_METRICS
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

const getFilterValues = ({ tasks }) => {
  const owners = [
    ...new Map(
      tasks.map(({ owner }) => {
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
      tasks.map(({ status }) => [
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
    ML_TASKS_FILTERS_NAMES.reduce(
      (params, queryKey) => ({
        ...params,
        [queryKey]: queryParams[queryKey]
      }),
      {}
    );
  return getFiltersRequestParams();
};

const MlTasks = ({ tasks, isLoading }) => {
  const [selectedFilters, setSelectedFilters] = useState(() => getRequestParams());

  useEffect(() => {
    updateQueryParams(selectedFilters);
  }, [selectedFilters]);

  const filteredData = useMemo(() => {
    const filters = Object.entries(selectedFilters).filter(([, filterValue]) => filterValue !== undefined);

    if (filters.length === 0) return tasks;

    return tasks.filter((task) =>
      filters.every((filter) => {
        const [filterType, filterValue] = filter;

        if (filterType === GOALS_FILTER) {
          if (!task.last_run_reached_goals || isEmptyObject(task.last_run_reached_goals)) {
            return false;
          }
          return Object.values(task.last_run_reached_goals).every(({ reached }) => reached) === filterValue;
        }

        if (filterType === OWNER_ID_FILTER) {
          if (filterValue === EMPTY_UUID) {
            return isEmptyObject(task.owner);
          }
          return task.owner.id === filterValue;
        }

        if (filterType === STATUS_BE_FILTER) {
          return task.status === filterValue;
        }

        return false;
      })
    );
  }, [tasks, selectedFilters]);

  const onFilterChange = (newFilters) => setSelectedFilters(newFilters);

  const filterValues = getFilterValues({ tasks });

  return (
    <>
      <PageActionBar />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            {isLoading ? (
              <TableLoader columnsCounter={4} showHeader />
            ) : (
              <MlTasksTable
                tasks={filteredData}
                appliedFilters={selectedFilters}
                filterValues={filterValues}
                onFilterChange={onFilterChange}
              />
            )}
          </div>
          <div>
            <InlineSeverityAlert messageId="mlTasksDescription" />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default MlTasks;
