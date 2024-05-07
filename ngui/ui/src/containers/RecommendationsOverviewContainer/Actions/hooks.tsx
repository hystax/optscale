import PlaylistRemoveOutlinedIcon from "@mui/icons-material/PlaylistRemoveOutlined";
import SettingsIcon from "@mui/icons-material/Settings";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import { ExcludePoolsFromRecommendationModal } from "components/SideModalManager/SideModals";
import { useDownloadCleanupScript } from "hooks/useDownloadCleanupScript";
import { useDownloadRecommendationItems } from "hooks/useDownloadRecommendationItems";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { DOWNLOAD_FILE_FORMATS } from "utils/constants";
import {
  useIsRecommendationPinned,
  usePinnedRecommendationsCount,
  useRecommendationPinActions
} from "../redux/pinnedRecommendations/hooks";

export const useSettingItems = (recommendation) => {
  const openSideModal = useOpenSideModal();

  const { withExclusions, hasSettings } = recommendation;

  return [
    ...(hasSettings
      ? [
          {
            key: "settings",
            Icon: SettingsIcon,
            body: <FormattedMessage id="settings" />,
            onClick: () =>
              openSideModal(recommendation.settingsSidemodalClass, {
                recommendationType: recommendation.type
              })
          }
        ]
      : []),
    ...(withExclusions
      ? [
          {
            key: "exclude",
            Icon: PlaylistRemoveOutlinedIcon,
            body: <FormattedMessage id="excludePools" />,
            onClick: () =>
              openSideModal(ExcludePoolsFromRecommendationModal, {
                recommendationName: recommendation.name,
                recommendationType: recommendation.type
              })
          }
        ]
      : [])
  ];
};

export const useDownloadCleanupScripts = (recommendation) => {
  const { type, hasItems, allDataSources } = recommendation;

  const { download, isLoading } = useDownloadCleanupScript({
    type
  });

  if (hasItems) {
    return allDataSources.map(({ name, type: dataSourceType, id }) => ({
      key: id,
      isLoading,
      body: <CloudLabel disableLink name={name} type={dataSourceType} />,
      onClick: () => download(id)
    }));
  }

  return [];
};

export const useDownloadItems = (recommendation, downloadLimit, selectedDataSources) => {
  const { type, items, status } = recommendation;

  const { download, isLoading } = useDownloadRecommendationItems({
    limit: downloadLimit,
    type,
    status,
    dataSourceIds: selectedDataSources
  });

  return isEmptyArray(items)
    ? []
    : [
        {
          key: "downloadXlsxFile",
          isLoading,
          body: <FormattedMessage id="downloadXlsxFile" />,
          onClick: () => download(DOWNLOAD_FILE_FORMATS.XLSX)
        },
        {
          key: "downloadJsonFile",
          isLoading,
          body: <FormattedMessage id="downloadJsonFile" />,
          onClick: () => download(DOWNLOAD_FILE_FORMATS.JSON)
        }
      ];
};

const MAX_PINNED_RECOMMENDATIONS = 5;

export const usePinItems = (recommendation) => {
  const isPinned = useIsRecommendationPinned(recommendation.type);

  const pinnedRecommendationsCount = usePinnedRecommendationsCount();

  const pinActions = useRecommendationPinActions(recommendation.type);

  if (isPinned) {
    return [
      {
        key: "unpin",
        body: <FormattedMessage id="unpin" />,
        onClick: () => {
          pinActions.unpin();
        }
      }
    ];
  }

  if (pinnedRecommendationsCount < MAX_PINNED_RECOMMENDATIONS) {
    return [
      {
        key: "pin",
        body: <FormattedMessage id="pin" />,
        onClick: () => {
          pinActions.pin();
        }
      }
    ];
  }

  return [];
};
