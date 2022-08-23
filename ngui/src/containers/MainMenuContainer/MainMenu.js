import React, { Fragment, useMemo } from "react";
import { ViewInArOutlined } from "@mui/icons-material";
import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import CalculateOutlinedIcon from "@mui/icons-material/CalculateOutlined";
import CloudOutlinedIcon from "@mui/icons-material/CloudOutlined";
import CloudSyncOutlinedIcon from "@mui/icons-material/CloudSyncOutlined";
import CurrencyExchangeOutlinedIcon from "@mui/icons-material/CurrencyExchangeOutlined";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import EventOutlined from "@mui/icons-material/EventOutlined";
import GroupWorkOutlinedIcon from "@mui/icons-material/GroupWorkOutlined";
import HiveIcon from "@mui/icons-material/Hive";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import LocalOfferIcon from "@mui/icons-material/LocalOffer";
import PeopleOutlinedIcon from "@mui/icons-material/PeopleOutlined";
import PublicIcon from "@mui/icons-material/Public";
import RestoreOutlinedIcon from "@mui/icons-material/RestoreOutlined";
import RunningWithErrorsOutlinedIcon from "@mui/icons-material/RunningWithErrorsOutlined";
import SettingsIcon from "@mui/icons-material/Settings";
import StorageOutlinedIcon from "@mui/icons-material/StorageOutlined";
import SyncAltOutlinedIcon from "@mui/icons-material/SyncAltOutlined";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import { List } from "@mui/material";
import { FormattedMessage } from "react-intl";
import MenuGroupWrapper from "components/MenuGroupWrapper";
import MenuItem from "components/MenuItem";
import ProductTour, { PRODUCT_TOUR } from "components/ProductTour";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import FinOpsChecklistIcon from "icons/FinOpsChecklistIcon";
import {
  ASSIGNMENT_RULE,
  ASSIGNMENT_RULES,
  ASSIGNMENT_RULE_CREATE,
  POOLS_BASE,
  ANOMALIES,
  CLUSTER_TYPES,
  CLUSTER_TYPE_CREATE,
  CLOUD_ACCOUNTS,
  USER_MANAGEMENT,
  USER_MANAGEMENT_BASE_URL,
  EVENTS,
  HOME,
  EXPENSES,
  CLOUD_EXPENSES_BASE,
  POOL_EXPENSES_BASE,
  OWNER_EXPENSES_BASE,
  POOL_EDIT_BASE,
  EXPENSES_MAP,
  RESOURCES,
  getPoolUrl,
  RECOMMENDATIONS,
  ARCHIVED_RECOMMENDATIONS,
  CLOUD_ACCOUNT_CONNECT,
  ENVIRONMENTS,
  ENVIRONMENT_CREATE,
  INTEGRATIONS,
  SETTINGS,
  QUOTAS_AND_BUDGETS,
  TAGGING_POLICIES,
  RESOURCE_LIFECYCLE,
  FINOPS_PORTAL,
  K8S_RIGHTSIZING,
  BUSINESS_INTELLIGENCE
} from "urls";
import { FILTER_BY, MENU_ITEM_ID, MENU_SECTIONS } from "utils/constants";

const getMenuItems = (organizationPoolId) => [
  {
    key: "sectionWithoutTitle",
    items: [
      {
        icon: HomeOutlinedIcon,
        id: MENU_ITEM_ID.HOME,
        messageId: "home",
        dataTestId: "btn_home",
        dataProductTourId: "home",
        link: HOME
      },
      {
        id: MENU_ITEM_ID.ENVIRONMENTS,
        icon: DnsOutlinedIcon,
        messageId: "environments",
        dataTestId: "btn_environments",
        dataProductTourId: "environments",
        link: ENVIRONMENTS,
        isActive: (currentPath) => currentPath.startsWith(ENVIRONMENTS) || currentPath.startsWith(ENVIRONMENT_CREATE)
      },
      {
        id: MENU_ITEM_ID.POOLS,
        icon: CalculateOutlinedIcon,
        messageId: "pools",
        link: getPoolUrl(organizationPoolId),
        dataTestId: "btn_pools",
        isActive: (currentPath) => currentPath.startsWith(`/${POOLS_BASE}`) || currentPath.startsWith(`${POOL_EDIT_BASE}/`),
        dataProductTourId: "pools"
      },
      {
        icon: StorageOutlinedIcon,
        id: MENU_ITEM_ID.RESOURCES,
        messageId: "resources",
        link: RESOURCES,
        dataTestId: "btn_resources",
        dataProductTourId: "resources",
        isActive: (currentPath) => currentPath.startsWith(RESOURCES)
      }
    ]
  },
  {
    sectionTitleMessageId: MENU_SECTIONS.OPTIMIZATION,
    key: MENU_SECTIONS.OPTIMIZATION,
    items: [
      {
        id: MENU_ITEM_ID.OPTIMIZATIONS,
        icon: ThumbUpAltOutlinedIcon,
        messageId: "recommendations",
        dataTestId: "btn_recommend",
        dataProductTourId: "recommendations",
        link: RECOMMENDATIONS
      },
      {
        id: MENU_ITEM_ID.ARCHIVED_OPTIMIZATIONS,
        icon: RestoreOutlinedIcon,
        messageId: "archive",
        dataTestId: "btn_recommend_archived",
        link: ARCHIVED_RECOMMENDATIONS
      },
      {
        id: MENU_ITEM_ID.K8S_RIGHTSIZING,
        icon: ViewInArOutlined,
        messageId: "k8sRightsizingTitle",
        dataTestId: "btn_k8s_rightsizing",
        link: K8S_RIGHTSIZING
      }
    ]
  },
  {
    sectionTitleMessageId: MENU_SECTIONS.FINOPS,
    key: MENU_SECTIONS.FINOPS,
    items: [
      {
        icon: BarChartOutlinedIcon,
        id: MENU_ITEM_ID.EXPENSES,
        messageId: "costExplorerTitle",
        link: EXPENSES,
        dataTestId: "btn_cost_explorer_page",
        isRootPath: (currentPath, currentQueryParams) =>
          currentPath === EXPENSES && currentQueryParams[FILTER_BY] === undefined,
        isActive: (currentPath) =>
          currentPath === EXPENSES ||
          currentPath.startsWith(`/${CLOUD_EXPENSES_BASE}`) ||
          currentPath.startsWith(`/${POOL_EXPENSES_BASE}`) ||
          currentPath.startsWith(`/${OWNER_EXPENSES_BASE}`)
      },
      {
        id: MENU_ITEM_ID.EXPENSES_MAP,
        icon: PublicIcon,
        messageId: "costMapTitle",
        dataTestId: "btn_cost_map",
        link: EXPENSES_MAP
      },
      {
        icon: FinOpsChecklistIcon,
        id: MENU_ITEM_ID.FINOPS_PORTAL,
        messageId: "finOpsPortalTitle",
        link: FINOPS_PORTAL,
        dataTestId: "btn_finops_portal"
      },
      {
        icon: HiveIcon,
        id: MENU_ITEM_ID.BUSINESS_INTELLIGENCE,
        messageId: "businessIntelligenceTitle",
        link: BUSINESS_INTELLIGENCE,
        dataTestId: "btn_business_intelligence"
      }
    ]
  },
  {
    sectionTitleMessageId: MENU_SECTIONS.POLICIES,
    key: MENU_SECTIONS.POLICIES,
    items: [
      {
        id: MENU_ITEM_ID.ANOMALIES,
        icon: RunningWithErrorsOutlinedIcon,
        messageId: "anomalyDetectionTitle",
        dataTestId: "btn_anomalies",
        link: ANOMALIES,
        isActive: (currentPath) => currentPath.startsWith(ANOMALIES)
      },
      {
        id: MENU_ITEM_ID.QUOTAS_AND_BUDGETS,
        icon: CurrencyExchangeOutlinedIcon,
        messageId: "quotasAndBudgetsTitle",
        dataTestId: "btn_quotas_and_budgets",
        link: QUOTAS_AND_BUDGETS,
        isActive: (currentPath) => currentPath.startsWith(QUOTAS_AND_BUDGETS)
      },
      {
        id: MENU_ITEM_ID.TAGGING_POLICIES,
        icon: LocalOfferIcon,
        messageId: "tagging",
        dataTestId: "btn_tagging_policies",
        link: TAGGING_POLICIES,
        isActive: (currentPath) => currentPath.startsWith(TAGGING_POLICIES)
      },
      {
        id: MENU_ITEM_ID.RESOURCE_LIFECYCLE,
        icon: CloudSyncOutlinedIcon,
        messageId: "resourceLifecycleTitle",
        dataTestId: "btn_resource_lifecycle",
        link: RESOURCE_LIFECYCLE,
        isActive: (currentPath) => currentPath.startsWith(RESOURCE_LIFECYCLE)
      },
      {
        id: MENU_ITEM_ID.ASSIGNMENT_RULES,
        icon: AssignmentOutlinedIcon,
        messageId: "assignmentRulesTitle",
        dataTestId: "btn_assignment_rules",
        link: ASSIGNMENT_RULES,
        isActive: (currentPath) =>
          currentPath.startsWith(ASSIGNMENT_RULE) ||
          currentPath.startsWith(ASSIGNMENT_RULES) ||
          currentPath.startsWith(ASSIGNMENT_RULE_CREATE)
      },
      {
        id: MENU_ITEM_ID.CLUSTER_TYPES,
        icon: GroupWorkOutlinedIcon,
        messageId: "clusterTypesTitle",
        dataTestId: "btn_cluster_types",
        link: CLUSTER_TYPES,
        isActive: (currentPath) => currentPath.startsWith(CLUSTER_TYPES) || currentPath.startsWith(CLUSTER_TYPE_CREATE)
      }
    ]
  },
  {
    sectionTitleMessageId: MENU_SECTIONS.SYSTEM,
    key: MENU_SECTIONS.SYSTEM,
    items: [
      {
        id: MENU_ITEM_ID.USER_MANAGEMENT,
        icon: PeopleOutlinedIcon,
        messageId: "userManagementTitle",
        link: USER_MANAGEMENT,
        dataTestId: "btn_user_management",
        dataProductTourId: "userManagement",
        isActive: (currentPath) => currentPath.startsWith(`/${USER_MANAGEMENT_BASE_URL}`)
      },
      {
        icon: CloudOutlinedIcon,
        id: MENU_ITEM_ID.CLOUD_ACCOUNTS,
        messageId: "dataSourcesTitle",
        link: CLOUD_ACCOUNTS,
        dataTestId: "btn_cloud_accs",
        dataProductTourId: "dataSources",
        isActive: (currentPath) => currentPath.startsWith(`${CLOUD_ACCOUNTS}`) || currentPath === CLOUD_ACCOUNT_CONNECT
      },
      {
        icon: SyncAltOutlinedIcon,
        id: MENU_ITEM_ID.INTEGRATIONS,
        messageId: "integrations",
        link: INTEGRATIONS,
        dataTestId: "btn_integrations"
      },
      {
        icon: EventOutlined,
        id: MENU_ITEM_ID.EVENTS,
        messageId: "events",
        link: EVENTS,
        dataTestId: "btn_events"
      },
      {
        icon: SettingsIcon,
        id: MENU_ITEM_ID.SETTINGS,
        messageId: "settings",
        link: SETTINGS,
        dataTestId: "btn_settings"
      }
    ]
  }
];

const MainMenu = () => {
  const { organizationPoolId } = useOrganizationInfo();

  const menuItems = useMemo(() => getMenuItems(organizationPoolId), [organizationPoolId]);

  const simpleItem = (menuItem) => (
    <MenuItem
      key={menuItem.id}
      className={menuItem.className}
      dataProductTourId={menuItem.dataProductTourId}
      link={menuItem.link}
      messageId={menuItem.messageId}
      fromMainMenu
      isRootPath={menuItem.isRootPath}
      isActive={menuItem.isActive}
      icon={menuItem.icon}
      dataTestId={menuItem.dataTestId}
    />
  );

  return (
    <>
      <ProductTour
        label={PRODUCT_TOUR}
        steps={[
          {
            content: <FormattedMessage id="homeProductTourContent" />,
            placement: "auto",
            disableBeacon: true,
            dataTestId: "p_tour_home",
            target: "[data-product-tour-id='home']"
          },
          {
            content: <FormattedMessage id="environmentsProductTourContent" />,
            placement: "auto",
            disableBeacon: true,
            dataTestId: "p_tour_environments",
            target: "[data-product-tour-id='environments']"
          },
          {
            content: <FormattedMessage id="recommendationsProductTourContent" />,
            placement: "auto",
            disableBeacon: true,
            dataTestId: "p_tour_recommendations",
            target: "[data-product-tour-id='recommendations']"
          },
          {
            content: <FormattedMessage id="resourcesProductTourContent" />,
            placement: "auto",
            disableBeacon: true,
            dataTestId: "p_tour_resources",
            target: "[data-product-tour-id='resources']"
          },
          {
            content: <FormattedMessage id="dataSourcesProductTourContent" />,
            placement: "auto",
            disableBeacon: true,
            dataTestId: "p_tour_data_source",
            target: "[data-product-tour-id='dataSources']"
          },
          {
            content: <FormattedMessage id="poolsProductTourContent" />,
            placement: "auto",
            disableBeacon: true,
            dataTestId: "p_tour_pools",
            target: "[data-product-tour-id='pools']"
          },
          {
            content: <FormattedMessage id="userManagementProductTourContent" />,
            placement: "auto",
            disableBeacon: true,
            dataTestId: "p_tour_user_management",
            showSkipButton: false,
            target: "[data-product-tour-id='userManagement']"
          }
        ]}
      />
      <List component="nav">
        {menuItems.map(({ items, sectionTitleMessageId, showSection, key }) => (
          <MenuGroupWrapper sectionTitleMessageId={sectionTitleMessageId} showSection={showSection} key={key} id={key}>
            {items.map(({ showItem = true, ...rest }) => showItem && simpleItem(rest))}
          </MenuGroupWrapper>
        ))}
      </List>
    </>
  );
};

export default MainMenu;
export { getMenuItems };
