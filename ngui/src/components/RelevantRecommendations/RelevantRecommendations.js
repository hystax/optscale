import React, { useMemo, useState } from "react";
import CachedOutlinedIcon from "@mui/icons-material/CachedOutlined";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import ErrorIcon from "@mui/icons-material/Error";
import SettingsIcon from "@mui/icons-material/Settings";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import { FormControlLabel, Stack } from "@mui/material";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";
import Accordion from "components/Accordion";
import ActionBar from "components/ActionBar";
import CloudLabel from "components/CloudLabel";
import ConditionWrapper from "components/ConditionWrapper";
import FormattedMoney from "components/FormattedMoney";
import Icon from "components/Icon";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel";
import PageContentWrapper from "components/PageContentWrapper";
import RecommendationAccordionTitle from "components/RecommendationAccordionTitle";
import RecommendationDescription from "components/RecommendationDescription";
import RecommendationFilters from "components/RecommendationFilters";
import RecommendationLimitWarning from "components/RecommendationLimitWarning";
import RecommendationsCategoriesButtonGroup from "components/RecommendationsCategoriesButtonGroup";
import SearchInput from "components/SearchInput";
import SummaryGrid from "components/SummaryGrid";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TabsWrapper from "components/TabsWrapper";
import TextWithDataTestId from "components/TextWithDataTestId";
import WrapperCard from "components/WrapperCard";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import { DOCS_HYSTAX_CLEANUP_SCRIPTS, getRecommendationSettingsUrl } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import {
  RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME,
  RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME,
  RECOMMENDATION_OBSOLETE_IMAGES,
  RECOMMENDATION_OBSOLETE_SNAPSHOTS,
  RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS,
  SUMMARY_VALUE_COMPONENT_TYPES,
  VOLUMES_NOT_ATTACHED_FOR_A_LONG_TIME_TYPE,
  INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME_TYPE,
  INSTANCE_MIGRATION_TYPE,
  OBSOLETE_SNAPSHOTS_TYPE,
  OBSOLETE_SNAPSHOT_CHAINS_TYPE,
  RESERVED_INSTANCES_TYPE,
  INSTANCE_SUBSCRIPTION_TYPE,
  RECOMMENDATIONS_TABS,
  RIGHTSIZING_INSTANCES_TYPE,
  RIGHTSIZING_RDS_INSTANCES_TYPE,
  ABANDONED_INSTANCES_TYPE,
  OBSOLETE_IPS_TYPE,
  SCOPE_TYPES,
  DOWNLOAD_FILE_FORMATS,
  ABANDONED_KINESIS_STREAMS_TYPE,
  PUBLIC_S3_BUCKETS_TYPE,
  ABANDONED_S3_BUCKETS_TYPE,
  INSTANCES_FOR_SHUTDOWN_TYPE,
  INSTANCES_GENERATION_UPGRADE_TYPE
} from "utils/constants";
import { getTimeDistance, getCurrentUTCTimeInSec } from "utils/datetime";
import { SPACING_1, SPACING_2 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";
import {
  getActiveRecommendationsByCategory,
  getDismissedRecommendationsByCategory,
  getExcludedRecommendationsByCategory
} from "utils/recommendationCategories";
import { abandonedInstancesRecommendation } from "./AbandonedInstances";
import { abandonedKinesisStreamsRecommendation } from "./AbandonedKinesisStreams";
import { abandonedS3BucketsRecommendation } from "./AbandonedS3Buckets";
import { inactiveConsoleUsersRecommendation } from "./InactiveConsoleUsers";
import { inactiveUsersRecommendation } from "./InactiveUsers";
import { insecureSecurityGroupsRecommendation } from "./InsecureSecurityGroups";
import { instancesForShutdownRecommendation } from "./InstancesForShutdown";
import { instancesGenerationUpgradeRecommendation } from "./InstancesGenerationUpgrade";
import { instancesInStoppedStateForALongTimeRecommendation } from "./InstancesInStoppedStateForALongTime";
import { instancesMigrationRecommendation } from "./InstancesMigration";
import { instanceSubscriptionRecommendation } from "./InstanceSubscription";
import { obsoleteImagesRecommendation } from "./ObsoleteImages";
import { obsoleteIpsRecommendation } from "./ObsoleteIps";
import { obsoleteSnapshotChainsRecommendation } from "./ObsoleteSnapshotChains";
import { obsoleteSnapshotsRecommendation } from "./ObsoleteSnapshots";
import { publicS3BucketsRecommendation } from "./PublicS3Buckets";
import { reservedInstancesRecommendation } from "./ReservedInstances";
import { rightsizingInstancesRecommendation } from "./RightsizingInstances";
import { rightsizingRdsInstancesRecommendation } from "./RightsizingRdsInstances";
import { shortLivingInstancesRecommendation } from "./ShortLivingInstances";
import { volumesNotAttachedForLongTimeRecommendation } from "./VolumesNotAttachedForLongTime";

const { ACTIVE: ACTIVE_RECOMMENDATIONS_TAB, DISMISSED: DISMISSED_TAB, EXCLUDED: EXCLUDED_TAB } = RECOMMENDATIONS_TABS;

const actionBarDefinition = {
  title: {
    messageId: "recommendations",
    dataTestId: "lbl_recommendations"
  }
};

const Saving = ({ saving }) => {
  const intlFormatter = useIntl();

  const monthTranslation = intlFormatter.formatMessage({ id: "month" }).toLowerCase();
  const perMonthTranslation = intlFormatter.formatMessage({ id: "perX" }, { x: monthTranslation }).toLowerCase();

  return (
    <KeyValueLabel
      messageId="savings"
      isBoldValue={false}
      value={() => (
        <>
          <strong>
            <FormattedMoney value={saving} />
          </strong>{" "}
          {perMonthTranslation}
        </>
      )}
    />
  );
};

const nextCheckRender = (nextRun) => {
  if (!nextRun) {
    return { id: "never" };
  }
  return {
    id: nextRun <= getCurrentUTCTimeInSec() ? "aboutToStart" : "valueIn",
    values: {
      value: nextRun <= getCurrentUTCTimeInSec() ? null : getTimeDistance(nextRun)
    }
  };
};

const getActionBarDownloadItem = ({
  type,
  moduleName,
  downloadRecommendation,
  isDownloadingRecommendation,
  buttonTestIds,
  items
}) => ({
  key: type,
  icon: <CloudDownloadOutlinedIcon fontSize="small" />,
  messageId: "download",
  type: "dropdown",
  dataTestId: isEmptyArray(buttonTestIds) ? null : buttonTestIds[0],
  isLoading: isDownloadingRecommendation,
  disabled: isEmptyArray(items),
  menu: {
    items: [
      {
        key: "xlsx",
        messageId: "xlsxFile",
        action: () => downloadRecommendation(moduleName, DOWNLOAD_FILE_FORMATS.XLSX)
      },
      {
        key: "json",
        messageId: "jsonFile",
        action: () => downloadRecommendation(moduleName, DOWNLOAD_FILE_FORMATS.JSON)
      }
    ]
  }
});

const getActionBarDropDownItem = ({ data, moduleName, downloadCleanupScript, isDownloadingCleanupScript, buttonTestIds }) => {
  const uniqueCloudAccounts = [...new Map(data.map((item) => [item.cloud_account_name, item])).values()];
  return {
    key: "clouds-add",
    icon: <DescriptionOutlinedIcon fontSize="small" />,
    messageId: "cleanupScripts",
    type: "dropdown",
    dataTestId: isEmptyArray(buttonTestIds) ? null : buttonTestIds[1],
    tooltip: {
      show: true,
      messageId: "cleanupScriptDescription",
      placement: "top",
      body: (
        <FormattedMessage
          id="cleanupScriptDescription"
          values={{
            link: (chunks) => (
              <Link href={DOCS_HYSTAX_CLEANUP_SCRIPTS} data-test-id="link_cleanup_script" target="_blank" rel="noopener">
                {chunks}
              </Link>
            )
          }}
        />
      )
    },
    disabled: isEmptyArray(data),
    isLoading: isDownloadingCleanupScript,
    menu: {
      items: isEmptyArray(uniqueCloudAccounts)
        ? [{ key: "empty" }]
        : uniqueCloudAccounts.map(({ cloud_account_name: name, cloud_type: type, cloud_account_id: id }) => ({
            key: id,
            text: <CloudLabel disableLink name={name} type={type} />,
            action: () => downloadCleanupScript(moduleName, id)
          }))
    }
  };
};

const getSetting = (selectedTab, { activeOptimizations, dismissedOptimizations, excludedRecommendations }) => {
  // TODO: icon, tooltipMessageId, dataTestIdPrefix are used only for dismiss/activate buttons, which is too specific
  // Perhaps we should change/update approach for render buttons
  // Current approach makes harder to add different buttons for different optimizations, or hide them.
  // To prevent rendering of the "activate/dismiss" buttons in the «Excluded» tab I've added «isEmpty(settings)» in the «getColumns» function
  if (selectedTab === EXCLUDED_TAB) {
    return {
      optimizations: excludedRecommendations
    };
  }
  if (selectedTab === DISMISSED_TAB) {
    return {
      icon: <VisibilityOutlinedIcon />,
      tooltipMessageId: "activateRecommendation",
      dataTestIdPrefix: "activate",
      optimizations: dismissedOptimizations
    };
  }
  return {
    icon: <VisibilityOffOutlinedIcon />,
    tooltipMessageId: "dismissRecommendation",
    dataTestIdPrefix: "dismiss",
    optimizations: activeOptimizations
  };
};

const TableWithLoadingAndMemo = ({ isLoading, table }) => {
  const { data, columns, ...rest } = table;
  const tableData = useMemo(() => data, [data]);
  const tableColumns = useMemo(() => columns, [columns]);
  return isLoading ? (
    <TableLoader columnsCounter={tableColumns.length} showHeader />
  ) : (
    <Table data={tableData} columns={tableColumns} {...rest} />
  );
};

const RecommendationAccordion = ({
  expanded,
  isGetRecommendationsLoading,
  handleChange,
  type,
  translatedType,
  count,
  saving,
  table,
  limit,
  descriptionMessageId,
  dataTestIds,
  error,
  options
}) => {
  const { isDemo } = useOrganizationInfo();
  return (
    <ConditionWrapper key={type} condition={isDemo && !!error}>
      <Accordion
        expanded={expanded[type]}
        onChange={() => handleChange(expanded[type] ? undefined : type)}
        disableExpandedSpacing
      >
        <ListItem data-test-id={dataTestIds.listTestId} button={false}>
          <RecommendationAccordionTitle
            messages={[
              <React.Fragment key={1}>{translatedType}</React.Fragment>,
              <KeyValueLabel key={2} messageId="count" value={count} />,
              saving && <Saving key={3} saving={saving} />
            ].filter(Boolean)}
          />
          {error ? (
            <ListItemIcon>
              <div style={{ display: "flex" }}>
                <Icon icon={ErrorIcon} color="error" tooltip={{ show: true, body: error }} hasLeftMargin />
              </div>
            </ListItemIcon>
          ) : null}
        </ListItem>
        {expanded[type] && (
          <Stack spacing={SPACING_1}>
            <RecommendationDescription
              messageId={descriptionMessageId}
              messageValues={{
                strong: (chunks) => <strong>{chunks}</strong>,
                daysThreshold: options?.days_threshold,
                cpuPercentThreshold: options?.cpu_percent_threshold,
                networkBpsThreshold: options?.network_bps_threshold,
                dataSizeAvg: options?.data_size_threshold,
                tier1RequestsQuantity: options?.tier_1_request_quantity_threshold,
                tier2RequestsQuantity: options?.tier_2_request_quantity_threshold,
                metricType: options?.metric?.type,
                metricLimit: options?.metric?.limit
              }}
              dataTestId={dataTestIds.textTestId}
              isLoading={isGetRecommendationsLoading}
            />
            {count > limit ? <RecommendationLimitWarning limit={limit} /> : null}
            {error ? (
              <Typography color="error">
                <FormattedMessage
                  id="recommendationError"
                  values={{
                    errorText: error
                  }}
                />
              </Typography>
            ) : null}
            <TableWithLoadingAndMemo isLoading={isGetRecommendationsLoading} table={table} />
          </Stack>
        )}
      </Accordion>
    </ConditionWrapper>
  );
};

const RecommendationAccordions = ({ optimizations, expanded, isGetRecommendationsLoading, handleChange }) =>
  optimizations.map((optimization) => {
    const { type, translatedType, count, saving, table, limit, descriptionMessageId, dataTestIds, error, options } =
      optimization;

    return (
      <RecommendationAccordion
        key={type}
        expanded={expanded}
        isGetRecommendationsLoading={isGetRecommendationsLoading}
        handleChange={handleChange}
        type={type}
        translatedType={translatedType}
        count={count}
        saving={saving}
        table={table}
        limit={limit}
        descriptionMessageId={descriptionMessageId}
        dataTestIds={dataTestIds}
        error={error}
        options={options}
      />
    );
  });

const ActiveRecommendationTabContent = ({
  expanded,
  isGetRecommendationsLoading,
  handleChange,
  optimizationsView,
  showEmpty
}) => {
  const optimizationsViewGroups = optimizationsView.reduce(
    (res, curr) => {
      if (curr.count !== 0) {
        return {
          ...res,
          shownGroup: [...res.shownGroup, curr]
        };
      }
      return {
        ...res,
        initiallyHiddenGroup: [...res.initiallyHiddenGroup, curr]
      };
    },
    {
      shownGroup: [],
      initiallyHiddenGroup: []
    }
  );

  const shownOptimizations = isEmptyArray(optimizationsViewGroups.shownGroup) ? null : (
    <RecommendationAccordions
      optimizations={optimizationsViewGroups.shownGroup}
      expanded={expanded}
      isGetRecommendationsLoading={isGetRecommendationsLoading}
      handleChange={handleChange}
    />
  );

  const initiallyHiddenOptimization = isEmptyArray(optimizationsViewGroups.initiallyHiddenGroup) ? null : (
    <RecommendationAccordions
      optimizations={optimizationsViewGroups.initiallyHiddenGroup}
      expanded={expanded}
      isGetRecommendationsLoading={isGetRecommendationsLoading}
      handleChange={handleChange}
    />
  );

  const emptyMessage =
    shownOptimizations || showEmpty ? null : (
      <div>
        <FormattedMessage id="noActiveRecommendationsAvailable" />
      </div>
    );

  return (
    <div>
      {emptyMessage}
      {shownOptimizations}
      {showEmpty && initiallyHiddenOptimization}
    </div>
  );
};

const RecommendationTabContent = ({ expanded, handleChange, optimizationsView, isGetRecommendationsLoading = false }) => (
  <RecommendationAccordions
    optimizations={optimizationsView}
    expanded={expanded}
    isGetRecommendationsLoading={isGetRecommendationsLoading}
    handleChange={handleChange}
  />
);

const getTableColumns = ({ columns, type, setting, patchResource, dataTestId, isGetResourceAllowedActionsLoading }) => {
  if (isEmptyObject(setting)) {
    return columns;
  }
  return columns.concat([
    {
      Header: (
        <TextWithDataTestId dataTestId={dataTestId}>
          <FormattedMessage id="actions" />
        </TextWithDataTestId>
      ),
      id: "actions",
      disableSortBy: true,
      Cell: ({
        row: {
          original: { resource_id: resourceId },
          index
        }
      }) => {
        const isAllowedAction = useIsAllowed({
          entityType: SCOPE_TYPES.RESOURCE,
          entityId: resourceId,
          requiredActions: ["MANAGE_RESOURCES", "MANAGE_OWN_RESOURCES"]
        });

        return (
          <IconButton
            icon={setting.icon}
            onClick={() => patchResource(resourceId, type)}
            isLoading={isGetResourceAllowedActionsLoading}
            disabled={!isAllowedAction}
            dataTestId={`btn_${type}_${setting.dataTestIdPrefix}_${index}`}
            tooltip={{
              show: true,
              value: <FormattedMessage id={isAllowedAction ? setting.tooltipMessageId : "youDoNotHaveEnoughPermissions"} />
            }}
          />
        );
      }
    }
  ]);
};

const RelevantRecommendations = ({
  data,
  isLoadingProps,
  handleAccordionsChange,
  downloadRecommendation,
  downloadCleanupScript,
  expanded,
  selectedTab,
  handleTabChange,
  patchResource,
  categorizedRecommendations,
  categoriesSizes,
  recommendationCategory,
  updateCategoryAndSelectedTab,
  applyFilterCallback,
  forceCheck
}) => {
  const {
    total_saving: totalSaving = 0,
    last_run: lastRun = 0,
    last_completed: lastCompleted = 0,
    next_run: nextRun = 0
  } = data;

  const navigate = useNavigate();

  const { isDemo } = useOrganizationInfo();

  const [showEmptyRecommendationsInActiveTab, setShowEmptyRecommendationsInActiveTab] = useState(false);

  const [search, setSearch] = useSyncQueryParamWithState("search", "");

  const {
    isGetRecommendationsLoading = false,
    isUpdateRecommendationsLoading = false,
    isGetResourceAllowedActionsLoading = false,
    isTabWrapperReady = false,
    isDownloadingRecommendation = false,
    isDownloadingCleanupScript = false
  } = isLoadingProps;

  const categorizedActiveRecommendations = getActiveRecommendationsByCategory(
    categorizedRecommendations,
    recommendationCategory
  );
  const categorizedDismissedRecommendations = getDismissedRecommendationsByCategory(
    categorizedRecommendations,
    recommendationCategory
  );

  const categorizedExcludedRecommendations = getExcludedRecommendationsByCategory(
    categorizedRecommendations,
    recommendationCategory
  );

  const { optimizations: optimizationsInSelectedTab, ...setting } = getSetting(selectedTab, {
    activeOptimizations: categorizedActiveRecommendations,
    dismissedOptimizations: categorizedDismissedRecommendations,
    excludedRecommendations: categorizedExcludedRecommendations
  });

  const isActiveOptimizationsEmpty = isEmptyObject(categorizedActiveRecommendations);
  const isDismissedOptimizationsEmpty = isEmptyObject(categorizedDismissedRecommendations);
  const isExcludedOptimizationsEmpty = isEmptyObject(categorizedExcludedRecommendations);

  const createRecommendation = (type) => {
    const create = {
      [inactiveUsersRecommendation.type]: () => inactiveUsersRecommendation.build(optimizationsInSelectedTab),
      [inactiveConsoleUsersRecommendation.type]: () => inactiveConsoleUsersRecommendation.build(optimizationsInSelectedTab),
      [shortLivingInstancesRecommendation.type]: () => shortLivingInstancesRecommendation.build(optimizationsInSelectedTab),
      [volumesNotAttachedForLongTimeRecommendation.type]: () => {
        const definition = volumesNotAttachedForLongTimeRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: VOLUMES_NOT_ATTACHED_FOR_A_LONG_TIME_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_vna_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [insecureSecurityGroupsRecommendation.type]: () => insecureSecurityGroupsRecommendation.build(optimizationsInSelectedTab),
      [instancesInStoppedStateForALongTimeRecommendation.type]: () => {
        const definition = instancesInStoppedStateForALongTimeRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_ind_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [instancesMigrationRecommendation.type]: () => {
        const definition = instancesMigrationRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: INSTANCE_MIGRATION_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_im_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [instancesForShutdownRecommendation.type]: () => {
        const definition = instancesForShutdownRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: INSTANCES_FOR_SHUTDOWN_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_ifs_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [instancesGenerationUpgradeRecommendation.type]: () => {
        const definition = instancesGenerationUpgradeRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: INSTANCES_GENERATION_UPGRADE_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_igu_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [obsoleteImagesRecommendation.type]: () => obsoleteImagesRecommendation.build(optimizationsInSelectedTab),
      [obsoleteSnapshotsRecommendation.type]: () => {
        const definition = obsoleteSnapshotsRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: OBSOLETE_SNAPSHOTS_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_os_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [obsoleteSnapshotChainsRecommendation.type]: () => {
        const definition = obsoleteSnapshotChainsRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: OBSOLETE_SNAPSHOT_CHAINS_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_osch_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [reservedInstancesRecommendation.type]: () => {
        const definition = reservedInstancesRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: RESERVED_INSTANCES_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_ri_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [instanceSubscriptionRecommendation.type]: () => {
        const definition = instanceSubscriptionRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: INSTANCE_SUBSCRIPTION_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_is_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [rightsizingInstancesRecommendation.type]: () => {
        const definition = rightsizingInstancesRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: RIGHTSIZING_INSTANCES_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_rightsizing_instances_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [rightsizingRdsInstancesRecommendation.type]: () => {
        const definition = rightsizingRdsInstancesRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: RIGHTSIZING_RDS_INSTANCES_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_rightsizing_rds_instances_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [abandonedInstancesRecommendation.type]: () => {
        const definition = abandonedInstancesRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: ABANDONED_INSTANCES_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_abandoned_instances_actions",
          isGetResourceAllowedActionsLoading
        });
        return definition;
      },
      [obsoleteIpsRecommendation.type]: () => {
        const definition = obsoleteIpsRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: OBSOLETE_IPS_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_obsolete_ips_actions"
        });
        return definition;
      },
      [abandonedKinesisStreamsRecommendation.type]: () => {
        const definition = abandonedKinesisStreamsRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: ABANDONED_KINESIS_STREAMS_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_abandoned_kinesis_streams_actions"
        });
        return definition;
      },
      [publicS3BucketsRecommendation.type]: () => {
        const definition = publicS3BucketsRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: PUBLIC_S3_BUCKETS_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_s3_public_buckets_actions"
        });
        return definition;
      },
      [abandonedS3BucketsRecommendation.type]: () => {
        const definition = abandonedS3BucketsRecommendation.build(optimizationsInSelectedTab);
        definition.columns = getTableColumns({
          columns: definition.columns,
          type: ABANDONED_S3_BUCKETS_TYPE,
          setting,
          patchResource,
          dataTestId: "lbl_abandoned_s3_buckets_actions"
        });
        return definition;
      }
    }[type];

    if (typeof create === "function") {
      return create();
    }

    return undefined;
  };

  const optimizationsSettings = Object.keys(optimizationsInSelectedTab)
    .map((type) => createRecommendation(type))
    .filter(Boolean);

  const getDefaultTableActionBarDefinition = ({ type, moduleName, buttonTestIds, items }) => [
    getActionBarDownloadItem({
      type: `download-${type}`,
      moduleName,
      downloadRecommendation,
      isDownloadingRecommendation,
      buttonTestIds,
      items
    })
  ];

  const getActionItems = ({ type, items, moduleName, dataTestIds }) => {
    const { buttonTestIds = [] } = dataTestIds;

    const actionBar = getDefaultTableActionBarDefinition({
      type,
      moduleName,
      buttonTestIds,
      items
    });

    if (selectedTab === ACTIVE_RECOMMENDATIONS_TAB) {
      const typesHasDownloadCleanup = [
        RECOMMENDATION_OBSOLETE_IMAGES,
        RECOMMENDATION_VOLUMES_NOT_ATTACHED_FOR_LONG_TIME,
        RECOMMENDATION_OBSOLETE_SNAPSHOTS,
        RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS,
        RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME
      ];

      if (typesHasDownloadCleanup.includes(type)) {
        actionBar.push(
          getActionBarDropDownItem({
            data: items,
            moduleName,
            downloadCleanupScript,
            isDownloadingCleanupScript,
            buttonTestIds
          })
        );
      }
    }

    if ([ACTIVE_RECOMMENDATIONS_TAB, EXCLUDED_TAB].includes(selectedTab)) {
      actionBar.unshift({
        key: "settings",
        icon: <SettingsIcon fontSize="small" />,
        messageId: "settings",
        action: () => navigate(getRecommendationSettingsUrl(type)),
        type: "button"
      });
    }

    return actionBar;
  };

  const optimizationsView = optimizationsSettings
    .filter(({ translatedType }) => translatedType.toLocaleLowerCase().includes(search.toLocaleLowerCase()))
    .map(
      ({
        type,
        translatedType,
        withExclusions,
        withThresholds,
        withRightsizingStrategy,
        withInsecurePorts,
        optimization: { count = 0, saving = 0, error = "", limit, items = [], category, options = {} },
        descriptionMessageId,
        columns,
        emptyMessageId,
        moduleName,
        dataTestIds
      }) => {
        const actionItems = getActionItems({
          type,
          items,
          moduleName,
          dataTestIds
        });

        return {
          type,
          translatedType,
          count,
          saving,
          category,
          error,
          limit,
          descriptionMessageId,
          dataTestIds,
          withExclusions,
          withThresholds,
          withRightsizingStrategy,
          withInsecurePorts,
          options,
          table: {
            data: items,
            columns,
            localization: {
              emptyMessageId
            },
            actionBar: {
              show: true,
              definition: {
                items: actionItems
              }
            }
          }
        };
      }
    )
    .sort((a, b) => b.saving - a.saving);

  const summaryData = [
    {
      key: "possibleMonthlySavings",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMoney,
      valueComponentProps: {
        value: totalSaving
      },
      dataTestIds: {
        cardTestId: "card_saving",
        titleTestId: "p_saving",
        valueTestId: "p_saving_value"
      },
      captionMessageId: "possibleMonthlySavings",
      isLoading: isGetRecommendationsLoading
    },
    {
      key: "lastCheckTime",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage,
      valueComponentProps: {
        id: !lastCompleted ? "never" : "valueAgo",
        values: {
          value: !lastCompleted ? null : getTimeDistance(lastCompleted)
        }
      },
      dataTestIds: {
        cardTestId: "card_last_check",
        titleTestId: "p_last_check",
        valueTestId: "p_last_time"
      },
      captionMessageId: "lastCheckTime",
      isLoading: isGetRecommendationsLoading || isUpdateRecommendationsLoading
    },
    {
      key: "nextCheckTime",
      valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.FormattedMessage,
      valueComponentProps:
        lastRun !== lastCompleted
          ? {
              id: "runningRightNow"
            }
          : nextCheckRender(nextRun),
      captionMessageId: "nextCheckTime",
      dataTestIds: {
        cardTestId: "card_next_check",
        titleTestId: "p_next_check",
        valueTestId: "p_next_time"
      },
      button: {
        show: !isDemo,
        icon: <CachedOutlinedIcon />,
        onClick: forceCheck,
        tooltip: {
          show: true,
          messageId: "forceCheck",
          placement: "top"
        }
      },
      isLoading: isGetRecommendationsLoading || isUpdateRecommendationsLoading
    }
  ];

  const renderTab = (render) =>
    isEmptyArray(optimizationsView) ? (
      <Box pt={1}>
        <FormattedMessage id="noRecommendations" />
      </Box>
    ) : (
      render({
        expanded,
        isGetRecommendationsLoading,
        handleChange: handleAccordionsChange,
        optimizationsView
      })
    );

  const activeRecommendationsTab = renderTab((commonTabContentProps) => (
    <ActiveRecommendationTabContent {...commonTabContentProps} showEmpty={showEmptyRecommendationsInActiveTab} />
  ));

  const recommendationTab = renderTab((commonTabContentProps) => <RecommendationTabContent {...commonTabContentProps} />);

  const tabs = [
    {
      title: ACTIVE_RECOMMENDATIONS_TAB,
      node: activeRecommendationsTab,
      renderCondition: () => !isActiveOptimizationsEmpty
    },
    {
      title: DISMISSED_TAB,
      node: recommendationTab,
      renderCondition: () => !isDismissedOptimizationsEmpty
    },
    {
      title: EXCLUDED_TAB,
      node: recommendationTab,
      renderCondition: () => !isExcludedOptimizationsEmpty
    }
  ];

  const renderRecommendations = () => (
    <TabsWrapper
      isLoading={!isTabWrapperReady}
      headerSx={{
        display: "flex",
        justifyContent: "space-between",
        flexDirection: {
          sm: "row",
          xs: "column"
        }
      }}
      headerAdornment={
        <Box display="flex">
          {selectedTab === ACTIVE_RECOMMENDATIONS_TAB && (
            <FormControlLabel
              control={
                <Switch
                  key="switch"
                  onChange={() => setShowEmptyRecommendationsInActiveTab(!showEmptyRecommendationsInActiveTab)}
                  checked={showEmptyRecommendationsInActiveTab}
                />
              }
              label={
                <Typography>
                  <FormattedMessage id="showEmpty" />
                </Typography>
              }
              labelPlacement="end"
            />
          )}
          <SearchInput
            onSearch={(searchText) => {
              setSearch(searchText);
              setShowEmptyRecommendationsInActiveTab(true);
            }}
            initialSearchText={search}
            sx={{
              marginTop: {
                xs: 2,
                sm: 0
              },
              alignSelf: "flex-end"
            }}
          />
        </Box>
      }
      tabsProps={{
        tabs,
        defaultTab: ACTIVE_RECOMMENDATIONS_TAB,
        activeTab: selectedTab,
        handleChange: handleTabChange,
        name: "optimizations"
      }}
    />
  );

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_2}>
          <Grid item>
            <SummaryGrid summaryData={summaryData} />
          </Grid>
          <Grid item xs={12}>
            <RecommendationFilters applyFilterCallback={applyFilterCallback} />
          </Grid>
          {isTabWrapperReady && lastCompleted === 0 ? (
            <Grid item xs={12}>
              <WrapperCard>
                <Typography>
                  <FormattedMessage id="recommendationProceeding" />
                </Typography>
              </WrapperCard>
            </Grid>
          ) : (
            <>
              <Grid item xs={12}>
                <RecommendationsCategoriesButtonGroup
                  categoriesSizes={categoriesSizes}
                  category={recommendationCategory}
                  onClick={updateCategoryAndSelectedTab}
                  isLoading={!isTabWrapperReady}
                />
              </Grid>
              <Grid item xs={12}>
                {renderRecommendations()}
              </Grid>
            </>
          )}
        </Grid>
      </PageContentWrapper>
    </>
  );
};

RecommendationTabContent.propTypes = {
  expanded: PropTypes.object,
  handleChange: PropTypes.func.isRequired,
  optimizationsView: PropTypes.array,
  isGetRecommendationsLoading: PropTypes.bool,
  withSettings: PropTypes.bool
};

TableWithLoadingAndMemo.propTypes = {
  table: PropTypes.object.isRequired,
  isLoading: PropTypes.bool
};

RelevantRecommendations.propTypes = {
  isLoadingProps: PropTypes.object,
  data: PropTypes.object.isRequired,
  handleAccordionsChange: PropTypes.func.isRequired,
  downloadRecommendation: PropTypes.func.isRequired,
  downloadCleanupScript: PropTypes.func.isRequired,
  selectedTab: PropTypes.string.isRequired,
  handleTabChange: PropTypes.func.isRequired,
  patchResource: PropTypes.func.isRequired,
  expanded: PropTypes.object,
  categorizedRecommendations: PropTypes.object,
  categoriesSizes: PropTypes.object,
  recommendationCategory: PropTypes.string,
  updateCategoryAndSelectedTab: PropTypes.func,
  applyFilterCallback: PropTypes.func,
  forceCheck: PropTypes.func
};

export default RelevantRecommendations;
