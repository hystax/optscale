import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { DropzoneForm } from "components/Dropzone";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

const FILE_TYPES = [
  "application/gzip",
  "application/x-gzip",
  "application/zip",
  "application/x-zip-compressed",
  "",
  "text/csv",
  ".csv",
];

const UploadCloudReportData = ({ onUpload, isLoading }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const canUpload = useIsAllowed({ requiredActions: ["MANAGE_CLOUD_CREDENTIALS"] });

  return canUpload ? (
    <DropzoneForm
      acceptedFiles={FILE_TYPES}
      onUpload={onUpload}
      isLoading={isLoading}
      isSubmitDisabled={isRestricted}
      submitButtonTooltip={{
        show: isRestricted,
        value: restrictionReasonMessage,
      }}
    />
  ) : (
    <Typography align="center" paragraph data-test-id="p_permissions">
      <FormattedMessage id="youDoNotHaveEnoughPermissions" />
    </Typography>
  );
};

export default UploadCloudReportData;
