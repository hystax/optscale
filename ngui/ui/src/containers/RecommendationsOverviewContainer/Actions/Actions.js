import React from "react";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import SyncProblemOutlinedIcon from "@mui/icons-material/SyncProblemOutlined";
import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import MailTo from "components/MailTo";
import Tooltip from "components/Tooltip";
import { DOCS_HYSTAX_CLEANUP_SCRIPTS, EMAIL_SALES } from "urls";
import { Menu } from "../RecommendationCard";
import { useDownloadCleanupScripts, useDownloadItems, usePinItems, useSettingItems } from "./hooks";

const DownloadCleanupScripts = ({ recommendation }) => {
  const downloadCleanupScripts = useDownloadCleanupScripts(recommendation);

  return (
    <Menu
      Icon={DescriptionOutlinedIcon}
      items={downloadCleanupScripts}
      tooltipMessage={
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
      }
    />
  );
};

const GeneralActions = ({ recommendation, withMenu }) => {
  const settingItems = useSettingItems(recommendation);
  const pinItems = usePinItems(recommendation);

  if (withMenu) {
    return <Menu Icon={MoreVertIcon} items={[...settingItems, ...pinItems]} />;
  }

  return settingItems.map(({ key, Icon, body, onClick }) => (
    <IconButton key={key} icon={<Icon />} onClick={onClick} tooltip={{ show: true, value: body }} />
  ));
};

const DownloadItems = ({
  recommendation,
  downloadLimit,
  isDownloadAvailable = false,
  isLoading = false,
  selectedDataSources
}) => {
  const downloadItems = useDownloadItems(recommendation, downloadLimit, selectedDataSources);

  return (
    <Menu
      tooltipMessage={
        isDownloadAvailable ? (
          <FormattedMessage id="downloadJsonXlsxFile" />
        ) : (
          <FormattedMessage
            id="recommendationDownloadFeatureIsUnavailable"
            values={{
              email: <MailTo email={EMAIL_SALES} text={EMAIL_SALES} />
            }}
          />
        )
      }
      Icon={CloudDownloadOutlinedIcon}
      items={downloadItems}
      disabled={!isDownloadAvailable}
      isLoading={isLoading}
    />
  );
};

const Actions = ({
  recommendation,
  downloadLimit,
  withMenu = false,
  isDownloadAvailable,
  isGetIsDownloadAvailableLoading,
  selectedDataSources
}) => {
  const { withCleanupScripts, hasItems } = recommendation;

  return (
    <Box display="flex">
      {withCleanupScripts && hasItems && <DownloadCleanupScripts recommendation={recommendation} />}
      {hasItems && (
        <DownloadItems
          recommendation={recommendation}
          downloadLimit={downloadLimit}
          isDownloadAvailable={isDownloadAvailable}
          isLoading={isGetIsDownloadAvailableLoading}
          selectedDataSources={selectedDataSources}
        />
      )}
      <GeneralActions recommendation={recommendation} withMenu={withMenu} />
      {!recommendation.optionsInSync && (
        <Tooltip title={<FormattedMessage id="recommendationsSettingsOutOfSyncMessage" />} placement="top">
          {/* wrap with span to enable tooltip on a disabled component */}
          <span>
            <IconButton icon={<SyncProblemOutlinedIcon color="info" />} disabled />
          </span>
        </Tooltip>
      )}
    </Box>
  );
};

export default Actions;
