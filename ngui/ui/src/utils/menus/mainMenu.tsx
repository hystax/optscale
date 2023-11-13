import MainMenuSectionTitle from "components/MainMenuSectionTitle";
import { MAIN_MENU_SECTION_IDS } from "components/MenuGroupWrapper/reducer";
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
import mlModels from "./mlModelMenuItem";
import mlRunsets from "./mlRunsetsMenuItem";
import pools from "./poolsMenuItem";
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
    items: [home, recommendations, resources, pools]
  },
  {
    id: MAIN_MENU_SECTION_IDS.FINOPS,
    menuSectionTitle: <MainMenuSectionTitle messageId="finops" />,
    items: [expenses, expensesMap, finOpsPortal]
  },
  {
    id: MAIN_MENU_SECTION_IDS.ML_OPS,
    menuSectionTitle: <MainMenuSectionTitle messageId="mlOps" />,
    items: [mlModels, mlRunsets]
  },
  {
    id: MAIN_MENU_SECTION_IDS.POLICIES,
    menuSectionTitle: <MainMenuSectionTitle messageId="policies" />,
    items: [anomalies, quotas, taggingPolicies, resourceLifecycle]
  },
  {
    id: MAIN_MENU_SECTION_IDS.SANDBOX,
    menuSectionTitle: <MainMenuSectionTitle messageId="sandbox" />,
    items: [environments, k8sRightsizing, recommendationsArchive, cloudCostComparisonMenuItem]
  },
  {
    id: MAIN_MENU_SECTION_IDS.SYSTEM,
    menuSectionTitle: <MainMenuSectionTitle messageId="system" />,
    items: [users, dataSources, integrations, events, settings]
  }
];
