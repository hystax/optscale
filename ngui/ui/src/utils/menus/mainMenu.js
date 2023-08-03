import React from "react";
import MainMenuSectionTitle from "components/MainMenuSectionTitle";
import MenuSectionBadge from "components/MenuSectionBadge";
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
import recommendations from "./recommendationsMenuItem";
import resourceLifecycle from "./resourceLifecycleMenuItem";
import resources from "./resourcesMenuItem";
import settings from "./settingsMenuItem";
import taggingPolicies from "./taggingPoliciesMenuItem";
import users from "./usersMenuItem";

export const MAIN_MENU_SECTION_IDS = Object.freeze({
  HOME: "home",
  FINOPS: "finops",
  ML_OPS: "mlOps",
  POLICIES: "policies",
  SYSTEM: "system"
});

export default [
  {
    id: MAIN_MENU_SECTION_IDS.HOME,
    items: [home, recommendations, resources, pools, environments]
  },
  {
    id: MAIN_MENU_SECTION_IDS.FINOPS,
    menuSectionTitle: <MainMenuSectionTitle messageId="finops" />,
    items: [expenses, expensesMap, finOpsPortal, k8sRightsizing, cloudCostComparisonMenuItem]
  },
  {
    id: MAIN_MENU_SECTION_IDS.ML_OPS,
    menuSectionBadge: <MenuSectionBadge messageId="beta" />,
    menuSectionTitle: <MainMenuSectionTitle messageId="mlOps" />,
    items: [mlModels, mlRunsets]
  },
  {
    id: MAIN_MENU_SECTION_IDS.POLICIES,
    menuSectionTitle: <MainMenuSectionTitle messageId="policies" />,
    items: [anomalies, quotas, taggingPolicies, resourceLifecycle]
  },
  {
    id: MAIN_MENU_SECTION_IDS.SYSTEM,
    menuSectionTitle: <MainMenuSectionTitle messageId="system" />,
    items: [users, dataSources, integrations, events, settings]
  }
];
