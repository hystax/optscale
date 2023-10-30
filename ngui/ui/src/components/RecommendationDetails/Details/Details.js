import React from "react";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import PlaylistRemoveIcon from "@mui/icons-material/PlaylistRemove";
import SettingsIcon from "@mui/icons-material/Settings";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { GET_RESOURCE_ALLOWED_ACTIONS } from "api/auth/actionTypes";
import CloudLabel from "components/CloudLabel";
import IconButton from "components/IconButton";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import ExcludePoolsFromRecommendationModal from "components/SideModalManager/SideModals/ExcludePoolsFromRecommendationModal";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ACTIVE, DISMISSED } from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import { useApiState } from "hooks/useApiState";
import { useDownloadCleanupScript } from "hooks/useDownloadCleanupScript";
import { useDownloadRecommendationItems } from "hooks/useDownloadRecommendationItems";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { DOCS_HYSTAX_CLEANUP_SCRIPTS } from "urls";
import { DOWNLOAD_FILE_FORMATS, SCOPE_TYPES } from "utils/constants";
import { isEmpty } from "utils/objects";
import RecommendationDetailsService from "../RecommendationDetailsService";

const useActionBarItems = ({ downloadLimit, recommendation, dataSourceIds, withDownload = false }) => {
  const openSideModal = useOpenSideModal();

  const { name, type, status, hasItems, hasSettings, items, isActive, isExcluded, withCleanupScripts, settingsSidemodalClass } =
    recommendation;

  const { download: downloadItems, isLoading: isDownloadLoading } = useDownloadRecommendationItems({
    limit: downloadLimit,
    type,
    status,
    dataSourceIds
  });

  const { download: downloadCleanupScript, isLoading: isDownloadCleanupScriptLoading } = useDownloadCleanupScript({ type });

  const actionBar = [
    {
      key: "download",
      startIcon: <CloudDownloadOutlinedIcon />,
      messageId: "download",
      type: "dropdown",
      dataTestId: `download`,
      isLoading: isDownloadLoading,
      disabled: !hasItems,
      show: withDownload,
      menu: {
        items: [
          {
            key: "xlsx",
            messageId: "xlsxFile",
            action: () => downloadItems(DOWNLOAD_FILE_FORMATS.XLSX)
          },
          {
            key: "json",
            messageId: "jsonFile",
            action: () => downloadItems(DOWNLOAD_FILE_FORMATS.JSON)
          }
        ]
      }
    }
  ];

  if (isActive && withCleanupScripts) {
    const uniqueCloudAccounts = [...new Map(items.map((item) => [item.cloud_account_name, item])).values()];

    actionBar.push({
      key: "cleanup-scripts",
      startIcon: <DescriptionOutlinedIcon />,
      messageId: "cleanupScripts",
      type: "dropdown",
      dataTestId: "btn-cleanup",
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
      disabled: !hasItems,
      isLoading: isDownloadCleanupScriptLoading,
      menu: {
        items: uniqueCloudAccounts.map(
          ({ cloud_account_name: dataSourceName, cloud_type: dataSourceType, cloud_account_id: dataSourceId }) => ({
            key: dataSourceId,
            text: <CloudLabel disableLink name={dataSourceName} type={dataSourceType} />,
            action: () => downloadCleanupScript(dataSourceId)
          })
        )
      }
    });
  }

  if (isExcluded) {
    actionBar.unshift({
      key: "exclude",
      icon: <PlaylistRemoveIcon fontSize="small" />,
      messageId: "excludePools",
      action: () => openSideModal(ExcludePoolsFromRecommendationModal, { recommendationName: name, recommendationType: type }),
      type: "button"
    });
  }

  if (isActive && hasSettings) {
    actionBar.unshift({
      key: "settings",
      icon: <SettingsIcon fontSize="small" />,
      messageId: "settings",
      action: () => openSideModal(settingsSidemodalClass, { recommendationType: type }),
      type: "button"
    });
  }

  return actionBar;
};

const ActionCell = ({ setting, resourceId, index, isGetResourceAllowedActionsLoading, patchResource }) => {
  const isAllowedAction = useIsAllowed({
    entityType: SCOPE_TYPES.RESOURCE,
    entityId: resourceId,
    requiredActions: ["MANAGE_RESOURCES", "MANAGE_OWN_RESOURCES"]
  });

  return (
    <IconButton
      icon={setting.icon}
      onClick={() => patchResource(resourceId)}
      isLoading={isGetResourceAllowedActionsLoading}
      disabled={!isAllowedAction}
      dataTestId={`btn_${setting.dataTestIdPrefix}_${index}`}
      tooltip={{
        show: true,
        value: <FormattedMessage id={isAllowedAction ? setting.tooltipMessageId : "youDoNotHaveEnoughPermissions"} />
      }}
    />
  );
};

const Details = ({ type, limit, status, data, dataSourceIds = [], withDownload }) => {
  const { usePatchResource } = RecommendationDetailsService();

  const patchResource = usePatchResource(type, status);

  const { isLoading: isGetResourceAllowedActionsLoading } = useApiState(GET_RESOURCE_ALLOWED_ACTIONS);

  const allRecommendations = useAllRecommendations();

  const recommendation = new allRecommendations[type](status, data);

  let columns = [...recommendation.columns];

  const actionBarItems = useActionBarItems({
    downloadLimit: limit,
    recommendation,
    dataSourceIds,
    withDownload
  });

  if (isEmpty(data)) {
    return null;
  }

  // TODO: Make this a computed class property
  if (recommendation.dismissable && (status === ACTIVE || status === DISMISSED)) {
    const setting =
      status === ACTIVE
        ? {
            icon: <VisibilityOffOutlinedIcon />,
            tooltipMessageId: "dismissRecommendation",
            dataTestIdPrefix: "dismiss"
          }
        : {
            icon: <VisibilityOutlinedIcon />,
            tooltipMessageId: "activateRecommendation",
            dataTestIdPrefix: "activate"
          };

    columns = [
      ...recommendation.columns,
      {
        header: (
          <TextWithDataTestId dataTestId="actions-header">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        enableSorting: false,
        cell: ({
          row: {
            original: { resource_id: resourceId },
            index
          }
        }) => (
          <ActionCell
            setting={setting}
            resourceId={resourceId}
            index={index}
            isGetResourceAllowedActionsLoading={isGetResourceAllowedActionsLoading}
            patchResource={(id) => patchResource(id)}
          />
        )
      }
    ];
  }

  return (
    <>
      {status === ACTIVE && (
        <InlineSeverityAlert
          messageId={recommendation.descriptionMessageId}
          messageValues={{ strong: (chunks) => <strong>{chunks}</strong>, ...recommendation.descriptionMessageValues }}
        />
      )}
      <Table
        actionBar={{
          show: true,
          definition: {
            items: actionBarItems
          }
        }}
        columns={columns}
        data={recommendation.items}
      />
    </>
  );
};

export default Details;
