import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import { Box, CircularProgress } from "@mui/material";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { REST_API_URL } from "api";
import MailTo from "components/MailTo";
import SubTitle from "components/SubTitle";
import TableCellActions from "components/TableCellActions";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { EMAIL_SUPPORT } from "urls";
import { SPACING_1 } from "utils/layouts";

const File = ({ filename, id, organizationId, index }) => {
  const { isFileDownloading, fetchAndDownload } = useFetchAndDownload();

  return (
    <Box display="inline-flex" alignItems="center">
      {filename}
      <TableCellActions
        items={[
          {
            key: "download",
            messageId: "download",
            icon: <CloudDownloadOutlinedIcon fontSize="small" />,
            dataTestId: `btn_download_${index}`,
            requiredActions: ["EDIT_PARTNER"],
            action: () => {
              fetchAndDownload({
                url: `${REST_API_URL}/organizations/${organizationId}/audit_results/${id}`,
                fallbackFilename: filename
              });
            },
            isLoading: isFileDownloading
          }
        ]}
      />
    </Box>
  );
};

const ResultFilesTable = ({ files, isLoading }) => {
  const { organizationId } = useOrganizationInfo();

  return (
    <>
      <SubTitle>
        <FormattedMessage id="technicalAuditReports" />
      </SubTitle>
      {isLoading ? (
        <CircularProgress size={20} />
      ) : (
        <>
          {files.length === 0 && <FormattedMessage id="technicalAudit.dataUnderProcessingNoFiles" />}
          <ul>
            {files.map(({ filename, id }, index) => (
              <li key={id}>
                <File filename={filename} id={id} organizationId={organizationId} index={index} />
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  );
};

const Description = ({ messageId }) => (
  <FormattedMessage
    id={messageId}
    values={{
      p: (chunks) => <p>{chunks}</p>,
      supportLink: (chunks) => <MailTo email={EMAIL_SUPPORT} text={chunks} />
    }}
  />
);

const DataUnderProcessing = () => {
  const { useGetTechnicalAudit } = OrganizationOptionsService();
  const {
    isGetTechnicalAuditLoading,
    options: { audit_results: files = [] }
  } = useGetTechnicalAudit();

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item>
        {/* TODO: probably need to remove p from app.json and component from here */}
        <Typography component="div">
          <Description messageId="technicalAudit.dataUnderProcessingPreDescription" />
          <ResultFilesTable files={files} isLoading={isGetTechnicalAuditLoading} />
          <Description messageId="technicalAudit.dataUnderProcessingPostDescription" />
        </Typography>
      </Grid>
    </Grid>
  );
};

export default DataUnderProcessing;
