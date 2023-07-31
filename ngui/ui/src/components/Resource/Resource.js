import React, { useState } from "react";
import AssignmentLateOutlinedIcon from "@mui/icons-material/AssignmentLateOutlined";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import GroupWorkOutlinedIcon from "@mui/icons-material/GroupWorkOutlined";
import LaunchOutlinedIcon from "@mui/icons-material/LaunchOutlined";
import MediationOutlinedIcon from "@mui/icons-material/MediationOutlined";
import ThumbUpAltOutlinedIcon from "@mui/icons-material/ThumbUpAltOutlined";
import { Link } from "@mui/material";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import ActionBarResourceNameTitleText from "components/ActionBarResourceNameTitleText";
import ClusterSubResourcesTable from "components/ClusterSubResourcesTable";
import EnvironmentBookings from "components/EnvironmentBookings";
import EnvironmentProperties from "components/EnvironmentProperties";
import PageContentWrapper from "components/PageContentWrapper";
import PaidNetworkTrafficLabel from "components/PaidNetworkTrafficLabel";
import ResourceConstraints from "components/ResourceConstraints";
import ResourceDetails from "components/ResourceDetails";
import ResourceExpenses from "components/ResourceExpenses";
import ResourceRecommendations from "components/ResourceRecommendations";
import { CiCdIntegrationModal, UnmarkEnvironmentModal } from "components/SideModalManager/SideModals";
import SummaryGrid from "components/SummaryGrid";
import TabsWrapper from "components/TabsWrapper";
import EnvironmentCostModelContainer from "containers/EnvironmentCostModelContainer";
import ResourceAllowedActionsContainer from "containers/ResourceAllowedActionsContainer";
import ResourceMetricsContainer from "containers/ResourceMetricsContainer";
import { useDataSources } from "hooks/useDataSources";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { RESOURCES, getCreateResourceAssignmentRuleUrl } from "urls";
import { trackEvent, GA_EVENT_CATEGORIES } from "utils/analytics";
import { isEmpty as isEmptyArray, getSumByObjectKey } from "utils/arrays";
import { SUMMARY_VALUE_COMPONENT_TYPES, RESOURCE_PAGE_TABS } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { getCloudResourceIdentifier, getResourceDisplayedName } from "utils/resources";

const {
  DETAILS: DETAILS_TAB,
  SUB_RESOURCES: SUB_RESOURCES_TAB,
  CONSTRAINTS: CONSTRAINTS_TAB,
  EXPENSES: EXPENSES_TAB,
  RECOMMENDATIONS: RECOMMENDATIONS_TAB,
  MONITORING: MONITORING_TAB,
  COST_MODEL: COST_MODEL_TAB,
  BOOKINGS: BOOKINGS_TAB
} = RESOURCE_PAGE_TABS;

const getTitleLogo = ({ cloudType, logo, imgDataTestId, clusterTypeId, isEnvironment, shareable }) => {
  if (clusterTypeId && shareable) {
    return {
      icon: [
        <DnsOutlinedIcon key="environment" data-test-id="img_title_environment_logo" />,
        <GroupWorkOutlinedIcon key="cluster" data-test-id="img_title_cluster_logo" />
      ]
    };
  }
  if (clusterTypeId) {
    return { icon: <GroupWorkOutlinedIcon data-test-id="img_title_cluster_logo" /> };
  }
  if (isEnvironment) {
    return { icon: <DnsOutlinedIcon data-test-id="img_title_environment_logo" /> };
  }
  return {
    src: logo,
    alt: cloudType,
    dataTestId: imgDataTestId
  };
};

const Resource = ({ resource, isGetResourceLoading, patchResource, isLoadingPatch }) => {
  const navigate = useNavigate();
  const openSideModal = useOpenSideModal();

  const [activeTab, setActiveTab] = useState();

  const {
    id,
    name,
    k8s_service: k8sService,
    k8s_namespace: k8sNamespace,
    k8s_node: k8sNode,
    resource_type: resourceType,
    details = {},
    tags,
    pool_id: poolId,
    recommendations: { modules = [] } = {},
    dismissed_recommendations: { modules: dismissedModules = [] } = {},
    employee_id: employeeId,
    // if cluster_type_id exists => this resource represents a cluster
    cluster_type_id: clusterTypeId,
    sub_resources: subResources = [],
    // if cluster_id exists => this resource is sub resource of a cluster
    cluster_id: clusterId,
    cloud_account_id: cloudAccountId,
    has_metrics: hasMetrics = false,
    is_environment: isEnvironment,
    shareable = false,
    env_properties: environmentProperties = {},
    ssh_only: isSshRequired = false,
    meta = {}
  } = resource;

  const { cloud_console_link: cloudConsoleLink } = meta;
  const {
    active = false,
    cloud_type: cloudType,
    first_seen: firstSeen,
    last_seen: lastSeen,
    cost = 0,
    total_cost: totalCost = 0,
    forecast = 0,
    constraints,
    policies,
    env_properties_collector_link: envPropertiesCollectorLink,
    total_traffic_expenses: totalTrafficExpenses = 0,
    total_traffic_usage: totalTrafficUsage = 0
  } = details;

  const savings = getSumByObjectKey(modules, "saving");

  const isPartOfCluster = !!clusterId;

  const { logo } = useDataSources(cloudType);

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={RESOURCES} component={RouterLink}>
        <FormattedMessage id="resources" />
      </Link>
    ],
    title: {
      text: () => {
        const resourceName = getResourceDisplayedName(resource);

        return (
          <ActionBarResourceNameTitleText
            resourceName={resourceName}
            renderTitleLabel={(fullResourceName) => <FormattedMessage id="detailsOf" values={{ title: fullResourceName }} />}
          />
        );
      },
      dataTestId: "lbl_resource_name",
      isLoading: isGetResourceLoading,
      logo: getTitleLogo({ cloudType, logo, imgDataTestId: `img_{cloud_type}`, clusterTypeId, isEnvironment, shareable })
    },
    items: [
      {
        key: "goToCloudConsole",
        icon: <LaunchOutlinedIcon fontSize="small" />,
        messageId: "goToCloudConsole",
        type: "button",
        href: cloudConsoleLink,
        show: !!cloudConsoleLink,
        dataTestId: "btn_cloud_console",
        isLoading: isGetResourceLoading
      },
      {
        key: "envPropertiesCollectorLink",
        icon: <MediationOutlinedIcon />,
        messageId: "cicdIntegration",
        type: "button",
        action: () => openSideModal(CiCdIntegrationModal, { envPropertiesCollectorLink }),
        show: !!envPropertiesCollectorLink,
        dataTestId: "btn_env_properties_collector_link",
        isLoading: isGetResourceLoading
      },
      {
        key: "assignmentRule",
        icon: <AssignmentLateOutlinedIcon fontSize="small" />,
        messageId: "addAssignmentRuleShort",
        type: "button",
        action: () => navigate(getCreateResourceAssignmentRuleUrl(id)),
        dataTestId: "btn_add_rule",
        show: !isPartOfCluster,
        isLoading: isGetResourceLoading
      },
      {
        key: "unmarkEnvironment",
        icon: <DnsOutlinedIcon fontSize="small" />,
        messageId: "unmarkEnvironment",
        type: "button",
        action: () => openSideModal(UnmarkEnvironmentModal, { name, id }),
        dataTestId: "btn_unmark_environment",
        requiredActions: ["MANAGE_RESOURCES"],
        show: !isEnvironment && shareable,
        isLoading: isGetResourceLoading
      }
    ]
  };

  const getSummaryData = [
    {
      key: "totalExpenses",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalCost
      },
      captionMessageId: "totalExpenses",
      isLoading: isGetResourceLoading,
      dataTestIds: {
        cardTestId: "card_total_exp"
      }
    },
    {
      key: "expensesThisMonth",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: cost
      },
      captionMessageId: "expensesThisMonth",
      isLoading: isGetResourceLoading,
      dataTestIds: {
        cardTestId: "card_exp_this_month"
      }
    },
    {
      key: "forecastThisMonth",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: forecast
      },
      captionMessageId: "forecastThisMonth",
      isLoading: isGetResourceLoading,
      dataTestIds: {
        cardTestId: "card_forecast_this_month"
      }
    },
    {
      key: "totalPaidNetworkTraffic",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
      CustomValueComponent: () => <PaidNetworkTrafficLabel cost={totalTrafficExpenses} usage={totalTrafficUsage} />,
      captionMessageId: "totalPaidNetworkTraffic",
      isLoading: isGetResourceLoading,
      dataTestIds: {
        cardTestId: "card_total_paid_network_traffic"
      }
    },
    {
      key: "possibleMonthlySavings",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: savings
      },
      captionMessageId: "possibleMonthlySavings",
      renderCondition: () => savings !== 0,
      button: {
        // Hide recommendations related button for clusters - "!clusterTypeId"
        show: !clusterTypeId,
        icon: <ThumbUpAltOutlinedIcon />,
        onClick: () => setActiveTab(RECOMMENDATIONS_TAB),
        tooltip: {
          show: true,
          messageId: "recommendations",
          placement: "top"
        }
      },
      isLoading: isGetResourceLoading || isLoadingPatch,
      dataTestIds: {
        cardTestId: "card_savings"
      }
    }
  ];

  const tabs = [
    {
      title: DETAILS_TAB,
      dataTestId: "tab_details",
      node: !!id && (
        <>
          {details.is_environment || shareable ? (
            <EnvironmentProperties environmentId={id} properties={environmentProperties} />
          ) : null}
          <ResourceDetails
            poolId={poolId}
            resourceType={resourceType}
            cloudResourceIdentifier={getCloudResourceIdentifier(resource)}
            name={name}
            tags={tags}
            subResources={subResources}
            clusterId={clusterId}
            clusterTypeId={clusterTypeId}
            serviceName={details.service_name}
            poolName={details.pool_name}
            poolType={details.pool_purpose}
            ownerName={details.owner_name}
            cloudName={details.cloud_name}
            cloudAccountId={cloudAccountId}
            cloudType={details.cloud_type}
            region={details.region}
            firstSeen={details.first_seen}
            lastSeen={details.last_seen}
            isActive={details.active}
            isEnvironment={details.is_environment}
            k8sService={k8sService}
            k8sNamespace={k8sNamespace}
            k8sNode={k8sNode}
            shareable={shareable}
            meta={meta}
          />
        </>
      )
    },
    {
      title: BOOKINGS_TAB,
      dataTestId: "tab_bookings",
      node: !!id && (
        <EnvironmentBookings
          resourceId={id}
          resourceName={name}
          isSshRequired={isSshRequired}
          poolId={poolId}
          poolName={details.pool_name}
          poolType={details.pool_purpose}
          resourceType={resourceType}
        />
      ),
      renderCondition: () => isEnvironment || shareable
    },
    {
      title: SUB_RESOURCES_TAB,
      dataTestId: "tab_sub_resources",
      node: !!id && <ClusterSubResourcesTable data={subResources} />,
      renderCondition: () => !!clusterTypeId
    },
    {
      title: CONSTRAINTS_TAB,
      dataTestId: "tab_constraints",
      node: !!id && (
        <ResourceConstraints
          employeeId={employeeId}
          poolId={poolId}
          constraints={constraints}
          poolPolicies={policies}
          isLoading={isGetResourceLoading}
          clusterId={clusterId}
          resourceId={id}
          billingOnly={!active}
          isResourceActive={active}
        />
      )
    },
    {
      title: COST_MODEL_TAB,
      dataTestId: "tab_cost_model",
      node: !!id && (
        <ResourceAllowedActionsContainer resourceId={id}>
          {({ isGetPermissionsLoading }) => (
            <EnvironmentCostModelContainer isGetPermissionsLoading={isGetPermissionsLoading} resourceId={id} />
          )}
        </ResourceAllowedActionsContainer>
      ),
      renderCondition: () => isEnvironment
    },
    {
      title: EXPENSES_TAB,
      dataTestId: "tab_expenses",
      node: !!id && (
        <ResourceExpenses
          firstSeen={firstSeen}
          lastSeen={lastSeen}
          resourceId={id}
          hasNetworkTrafficExpenses={totalTrafficExpenses !== 0 || totalTrafficUsage !== 0}
        />
      )
    },
    {
      title: RECOMMENDATIONS_TAB,
      dataTestId: "tab_recommendations",
      node: !!id && (
        <ResourceAllowedActionsContainer resourceId={id}>
          {({ isGetPermissionsLoading }) => (
            <ResourceRecommendations
              patchResource={patchResource}
              dismissedRecommendations={dismissedModules}
              recommendations={modules}
              resourceId={id}
              isLoading={isGetPermissionsLoading}
            />
          )}
        </ResourceAllowedActionsContainer>
      ),
      // Temporary hide recommendations for clusters - "!clusterTypeId"
      renderCondition: () => !clusterTypeId && !(isEmptyArray(modules) && isEmptyArray(dismissedModules))
    },
    {
      title: MONITORING_TAB,
      dataTestId: "tab_monitoring",
      node: !!id && <ResourceMetricsContainer resourceId={id} firstSeen={firstSeen} lastSeen={lastSeen} />,
      renderCondition: () => hasMetrics
    }
  ];

  const handleChange = (event, value) => {
    setActiveTab(value);
    if (value === BOOKINGS_TAB) {
      trackEvent({ category: GA_EVENT_CATEGORIES.ENVIRONMENT, action: "Clicked bookings tab" });
    }
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_2}>
          <Grid container item xs={12}>
            <SummaryGrid summaryData={getSummaryData} />
          </Grid>
          <Grid item xs={12}>
            <TabsWrapper
              isLoading={isGetResourceLoading || isLoadingPatch}
              tabsProps={{
                tabs,
                defaultTab: DETAILS_TAB,
                activeTab,
                handleChange,
                name: "resources-details"
              }}
            />
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

Resource.propTypes = {
  resource: PropTypes.object.isRequired,
  isGetResourceLoading: PropTypes.bool,
  isLoadingPatch: PropTypes.bool,
  patchResource: PropTypes.func
};

export default Resource;
