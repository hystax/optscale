import { useCallback, useMemo, useState } from "react";
import { useIntl } from "react-intl";
import { useTaskRunsDashboardState } from "reducers/taskRunsDashboard/useTaskRunsDashboardState";
import LayoutsService from "services/LayoutsService";
import { getIntersection } from "utils/arrays";
import { LAYOUT_TYPES } from "utils/constants";

export const GRID_TYPES = Object.freeze({
  ONE_COLUMN: 0,
  TWO_COLUMN: 1,
  THREE_COLUMNS: 2
});

export const DEFAULT_DASHBOARD = {
  id: "default",
  name: "Default",
  data: {
    charts: [
      {
        id: 1,
        name: "Report 1",
        breakdowns: ["host_ram", "host_cpu", "process_cpu", "process_ram", "gpu_load", "gpu_memory_used"]
      }
    ],
    show_milestones: true,
    sync_tooltips: true,
    grid_type: GRID_TYPES.ONE_COLUMN
  }
};

export const isDefaultDashboard = (dashboardId) => dashboardId === DEFAULT_DASHBOARD.id;

const useBreakdownChartActions = ({ charts, implementedMetricsBreakdownNames, setDashboard, setSaved }) => {
  const intl = useIntl();

  const maxChartId = charts.length ? charts.at(-1).id : 0;

  const createChart = useCallback(
    (id) => ({
      id,
      name: `${intl.formatMessage({ id: "report" })} ${id}`,
      breakdowns: implementedMetricsBreakdownNames
    }),
    [implementedMetricsBreakdownNames, intl]
  );

  const addChart = () => {
    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        charts: [...currentDashboard.data.charts, createChart(maxChartId + 1)]
      }
    }));
    setSaved(false);
  };

  const removeChart = (idToRemove) => {
    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        charts: currentDashboard.data.charts.filter(({ id }) => id !== idToRemove)
      }
    }));
    setSaved(false);
  };

  const cloneChart = (id) => {
    const getChartCopy = (idToCopy) => {
      const chartToCopy = charts.find(({ id: chartId }) => chartId === idToCopy);
      const { breakdowns, name } = chartToCopy;
      return { id: maxChartId + 1, name: `Clone of ${name}`, breakdowns: [...breakdowns] };
    };

    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        charts: [...currentDashboard.data.charts, getChartCopy(id)]
      }
    }));
    setSaved(false);
  };

  const updateChartName = (chartId, name) => {
    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        charts: currentDashboard.data.charts.map((chart) => {
          if (chart.id === chartId) {
            return { ...chart, name };
          }
          return chart;
        })
      }
    }));
    setSaved(false);
  };

  const updateChartBreakdowns = (chartId, breakdowns) => {
    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        charts: currentDashboard.data.charts.map((chart) => {
          if (chart.id === chartId) {
            return { ...chart, breakdowns };
          }
          return chart;
        })
      }
    }));
    setSaved(false);
  };

  return {
    addChart,
    removeChart,
    cloneChart,
    updateChartName,
    updateChartBreakdowns
  };
};

const useMilestoneActions = ({ setSaved, setDashboard }) => {
  const enableMilestones = () => {
    setSaved(false);
    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        show_milestones: true
      }
    }));
  };

  const disableMilestones = () => {
    setSaved(false);
    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        show_milestones: false
      }
    }));
  };

  return {
    enableMilestones,
    disableMilestones
  };
};

const useTooltipSyncActions = ({ setSaved, setDashboard }) => {
  const enableTooltipSync = () => {
    setSaved(false);
    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        sync_tooltips: true
      }
    }));
  };

  const disableTooltipSync = () => {
    setSaved(false);
    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        sync_tooltips: false
      }
    }));
  };

  return {
    enableTooltipSync,
    disableTooltipSync
  };
};

const useGridTypeActions = ({ setSaved, setDashboard }) => {
  const updateGridType = (gridType) => {
    setSaved(false);
    setDashboard((currentDashboard) => ({
      ...currentDashboard,
      data: {
        ...currentDashboard.data,
        grid_type: gridType
      }
    }));
  };

  return { updateGridType };
};

export const useModelRunChartState = ({ taskId, implementedMetricsBreakdownNames, breakdownNames }) => {
  const { dashboardId: selectedDashboardId, setDashboardId: setSelectedDashboardId } = useTaskRunsDashboardState(taskId);

  const { useGetAll, useGetOneOnDemand, useUpdate, useDelete, useCreate } = LayoutsService();
  const { onGet, layout, isLoading: isGetOneLoading } = useGetOneOnDemand();
  const { onDelete } = useDelete();
  const { onCreate } = useCreate();
  const { onUpdate } = useUpdate();

  const [saved, setSaved] = useState(true);

  const initializeDashboardState = useCallback(
    (dashboard) => {
      const data = dashboard.id === "default" ? dashboard.data : JSON.parse(dashboard.data);

      return {
        id: dashboard.id,
        name: dashboard.name,
        ownerId: dashboard.owner_id,
        shared: dashboard.shared,
        data: {
          show_milestones: data?.show_milestones ?? true,
          sync_tooltips: data?.sync_tooltips ?? true,
          grid_type: data?.grid_type ?? GRID_TYPES.ONE_COLUMN,
          charts:
            data?.charts?.map((chart) => ({
              ...chart,
              breakdowns: getIntersection(breakdownNames, chart.breakdowns)
            })) ?? []
        }
      };
    },
    [breakdownNames]
  );

  const [dashboard, setDashboard] = useState(() => {
    if (layout.id === selectedDashboardId) {
      return initializeDashboardState(layout);
    }
    return initializeDashboardState(DEFAULT_DASHBOARD);
  });

  const getAllLayoutsApiParams = useMemo(
    () => ({
      layoutType: LAYOUT_TYPES.ML_RUN_CHARTS_DASHBOARD,
      entityId: taskId,
      includeShared: true
    }),
    [taskId]
  );

  const onSuccessGetAllLayouts = useCallback(
    ({ layouts: apiLayouts }) => {
      if (selectedDashboardId === DEFAULT_DASHBOARD.id) {
        setDashboard(initializeDashboardState(DEFAULT_DASHBOARD));
      }
      if (apiLayouts.find(({ id }) => id === selectedDashboardId)) {
        onGet(selectedDashboardId).then((dashboardInfo) => {
          setDashboard(initializeDashboardState(dashboardInfo));
        });
      }
    },
    [initializeDashboardState, onGet, selectedDashboardId]
  );

  const { layouts, currentEmployeeId, isLoading: isGetAllLoading } = useGetAll(getAllLayoutsApiParams, onSuccessGetAllLayouts);

  const onDashboardChange = (newDashboardId) => {
    setSaved(true);

    if (isDefaultDashboard(newDashboardId)) {
      setDashboard(initializeDashboardState(DEFAULT_DASHBOARD));
      setSelectedDashboardId(newDashboardId);
    } else {
      onGet(newDashboardId).then((dashboardInfo) => {
        setDashboard(initializeDashboardState(dashboardInfo));
        setSelectedDashboardId(newDashboardId);
      });
    }
  };

  const createDashboard = ({ name, shared }) =>
    onCreate({
      name,
      shared,
      data: JSON.stringify(dashboard.data),
      entityId: taskId,
      type: LAYOUT_TYPES.ML_RUN_CHARTS_DASHBOARD
    }).then((apiData) => {
      setSaved(true);
      setSelectedDashboardId(apiData.id);
    });

  const updateDashboard = ({ name, shared }) =>
    onUpdate(dashboard.id, {
      name,
      shared,
      data: JSON.stringify(dashboard.data)
    }).then(() => {
      setSaved(true);
    });

  const removeDashboard = (id) =>
    onDelete(id).then(() => {
      setSaved(true);
      setSelectedDashboardId(DEFAULT_DASHBOARD.id);
    });

  const { addChart, removeChart, cloneChart, updateChartName, updateChartBreakdowns } = useBreakdownChartActions({
    charts: dashboard.data.charts,
    implementedMetricsBreakdownNames,
    setDashboard,
    setSaved
  });

  const { enableMilestones, disableMilestones } = useMilestoneActions({ setDashboard, setSaved });

  const { enableTooltipSync, disableTooltipSync } = useTooltipSyncActions({ setDashboard, setSaved });

  const { updateGridType } = useGridTypeActions({ setDashboard, setSaved });

  return {
    currentEmployeeId,
    dashboard: {
      ...dashboard,
      data: {
        ...DEFAULT_DASHBOARD.data,
        ...dashboard.data
      }
    },
    dashboards: [DEFAULT_DASHBOARD, ...layouts],
    onDashboardChange,
    //
    saved,
    //
    addChart,
    cloneChart,
    removeChart,
    updateChartBreakdowns,
    updateChartName,
    //
    updateDashboard,
    removeDashboard,
    createDashboard,
    //
    enableMilestones,
    disableMilestones,
    //
    enableTooltipSync,
    disableTooltipSync,
    //
    updateGridType,
    //
    isLoadingProps: {
      isSetupLoading: isGetAllLoading,
      isSelectNewLoading: isGetOneLoading
    }
  };
};
