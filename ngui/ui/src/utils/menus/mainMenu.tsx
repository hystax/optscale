import MainMenuSectionTitle from "components/MainMenuSectionTitle";
import { MAIN_MENU_SECTION_IDS } from "components/MenuGroupWrapper/reducer";
import { OPTSCALE_MODE } from "utils/constants";
import anomalies from "./anomaliesMenuItem";
import cloudCostComparisonMenuItem from "./cloudCostComparisonMenuItem";
import dataSources from "./dataSourcesMenuItem";
import environments from "./environmentsMenuItem";
import events from "./eventsMenuItem";
import expensesMap from "./expensesMapMenuItem";
import expenses from "./expensesMenuItem";
import finOpsPortal from "./finOpsPortalMenuItem";
import home from "./homeMenuItem";
import integrations from "./integrationsMenuItem";
import k8sRightsizing from "./k8sRightsizingMenuItem";
import mlDatasets from "./mlDatasetsMenuItem";
import mlHypertuningMenuItem from "./mlHypertuningMenuItem";
import mlModels from "./mlModelsMenuItem";
import mlTasks from "./mlTasksMenuItem";
import pools from "./poolsMenuItem";
import powerSchedulesMenuItem from "./powerSchedulesMenuItem";
import quotas from "./quotasMenuItem";
import recommendationsArchive from "./recommendationsArchiveMenuItem";
import recommendations from "./recommendationsMenuItem";
import resourceLifecycle from "./resourceLifecycleMenuItem";
import resources from "./resourcesMenuItem";
import settings from "./settingsMenuItem";
import taggingPolicies from "./taggingPoliciesMenuItem";
import users from "./usersMenuItem";

export default [
  {
    id: MAIN_MENU_SECTION_IDS.HOME,
    items: [home, recommendations, resources, pools, environments]
  },
  {
    id: MAIN_MENU_SECTION_IDS.FINOPS,
    menuSectionTitle: <MainMenuSectionTitle messageId="finops" />,
    items: [expenses, expensesMap, finOpsPortal],
    mode: OPTSCALE_MODE.FINOPS
  },
  {
    id: MAIN_MENU_SECTION_IDS.ML_OPS,
    menuSectionTitle: <MainMenuSectionTitle messageId="mlops" />,
    items: [mlTasks, mlModels, mlDatasets, mlHypertuningMenuItem]
  },
  {
    id: MAIN_MENU_SECTION_IDS.POLICIES,
    menuSectionTitle: <MainMenuSectionTitle messageId="policies" />,
    items: [anomalies, quotas, taggingPolicies, resourceLifecycle, powerSchedulesMenuItem],
    mode: OPTSCALE_MODE.FINOPS
  },
  {
    id: MAIN_MENU_SECTION_IDS.SANDBOX,
    menuSectionTitle: <MainMenuSectionTitle messageId="sandbox" />,
    items: [k8sRightsizing, recommendationsArchive, cloudCostComparisonMenuItem],
    mode: OPTSCALE_MODE.FINOPS
  },
  {
    id: MAIN_MENU_SECTION_IDS.SYSTEM,
    menuSectionTitle: <MainMenuSectionTitle messageId="system" />,
    items: [users, dataSources, integrations, events, settings]
  }
];
