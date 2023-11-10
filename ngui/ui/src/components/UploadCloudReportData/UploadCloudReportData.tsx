import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { DropzoneForm } from "components/Dropzone";
import { useIsAllowed } from "hooks/useAllowedActions";

const FILE_TYPES = [
  "application/gzip",
  "application/x-gzip",
  "application/zip",
  "application/x-zip-compressed",
  "",
  "text/csv",
  ".csv"
];

const UploadCloudReportData = ({ onUpload, isLoading }) => {
  const canUpload = useIsAllowed({ requiredActions: ["MANAGE_CLOUD_CREDENTIALS"] });

  return canUpload ? (
    <DropzoneForm acceptedFiles={FILE_TYPES} onUpload={onUpload} isLoading={isLoading} />
  ) : (
    <Typography align="center" paragraph data-test-id="p_permissions">
      <FormattedMessage id="youDoNotHaveEnoughPermissions" />
    </Typography>
  );
};

export default UploadCloudReportData;
