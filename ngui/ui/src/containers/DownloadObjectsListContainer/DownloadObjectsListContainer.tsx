import { useState } from "react";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { REST_API_URL } from "api";
import ButtonLoader from "components/ButtonLoader";
import SnackbarAlert from "components/SnackbarAlert";
import {
  useGeminiDataPreparationLazyQuery,
  useScheduleGeminiDataPreparationMutation,
} from "graphql/__generated__/hooks/restapi";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MILLISECONDS_IN_SECOND, SECONDS_IN_MINUTE } from "utils/datetime";
import { DownloadObjectsListContainerProps } from "./types";

const POLL_INTERVAL_MS = 2 * MILLISECONDS_IN_SECOND;
const POLL_TIMEOUT_MS = 2 * SECONDS_IN_MINUTE * MILLISECONDS_IN_SECOND;

const sleep = (ms: number) =>
  new Promise<void>((resolve) => {
    setTimeout(resolve, ms);
  });

const GEMINI_DATA_PREPARATION_STATUS = {
  SUCCESS: "SUCCESS",
  FAILED: "FAILED",
};

const DownloadObjectsListContainer = ({ fromBucketName, toBucketName, checkId }: DownloadObjectsListContainerProps) => {
  const { isDemo } = useOrganizationInfo();
  const { isFileDownloading, fetchAndDownload } = useFetchAndDownload();

  const [isGenerating, setIsGenerating] = useState(false);
  const [errorAlert, setErrorAlert] = useState<{ open: boolean; messageId: string }>({
    open: false,
    messageId: "downloadObjectsListGenerationError",
  });

  const showErrorAlert = (messageId: string) => {
    setErrorAlert({ open: true, messageId });
  };

  const [scheduleGeminiDataPreparation] = useScheduleGeminiDataPreparationMutation();

  const [fetchGeminiDataPreparation] = useGeminiDataPreparationLazyQuery({
    fetchPolicy: "network-only",
  });

  const downloadObjectsList = async () => {
    if (isGenerating || isFileDownloading) {
      return;
    }

    const buckets = Array.from(new Set([fromBucketName, toBucketName]));

    try {
      setIsGenerating(true);

      const { data: scheduleData } = await scheduleGeminiDataPreparation({
        variables: { geminiId: checkId, buckets },
      });

      const preparationId = scheduleData?.scheduleGeminiDataPreparation?.id;

      if (!preparationId) {
        showErrorAlert("downloadObjectsListGenerationError");
        return;
      }

      const startTime = Date.now();

      while (true) {
        const { data } = await fetchGeminiDataPreparation({
          variables: { id: preparationId },
        });

        const status = data?.geminiDataPreparation?.status;

        if (status === GEMINI_DATA_PREPARATION_STATUS.SUCCESS) {
          fetchAndDownload({
            url: `${REST_API_URL}/geminis_data/${preparationId}/download`,
            fallbackFilename: "objects_list.csv",
          });
          break;
        }

        if (status === GEMINI_DATA_PREPARATION_STATUS.FAILED) {
          showErrorAlert("downloadObjectsListGenerationFailed");
          break;
        }

        if (Date.now() - startTime > POLL_TIMEOUT_MS) {
          showErrorAlert("downloadObjectsListGenerationTimedOut");
          break;
        }

        await sleep(POLL_INTERVAL_MS);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const getButtonMessageId = () => {
    if (isFileDownloading) {
      return "downloadObjectsListDownloading";
    }
    if (isGenerating) {
      return "downloadObjectsListPreparing";
    }
    return "downloadObjectsList";
  };

  return (
    <Box>
      <SnackbarAlert
        body={<FormattedMessage id={errorAlert.messageId} />}
        openState={errorAlert.open}
        severity="error"
        handleClose={() => setErrorAlert((state) => ({ ...state, open: false }))}
      />
      <ButtonLoader
        sx={{ whiteSpace: "nowrap", minWidth: "210px" }}
        messageId={getButtonMessageId()}
        startIcon={<CloudDownloadOutlinedIcon />}
        onClick={() => downloadObjectsList()}
        color="primary"
        variant="contained"
        isLoading={isGenerating || isFileDownloading}
        disabled={isDemo}
        tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
      />
    </Box>
  );
};

export default DownloadObjectsListContainer;
