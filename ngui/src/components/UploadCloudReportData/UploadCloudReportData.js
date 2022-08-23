import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Upload from "components/Upload";
import { useIsAllowed } from "hooks/useAllowedActions";
import { isEmpty } from "utils/arrays";
import { SUCCESS } from "utils/constants";
import { isCloudReportExtensionSupported } from "utils/files";
import { SPACING_6 } from "utils/layouts";

const UploadCloudReportData = ({ onUpload, sendState, isLoading }) => {
  const [errorText, setErrorText] = useState();
  const [files, setFiles] = useState();

  const canUpload = useIsAllowed({ requiredActions: ["MANAGE_CLOUD_CREDENTIALS"] });

  useEffect(() => {
    if (sendState === SUCCESS) {
      setErrorText("");
    }
  }, [sendState]);

  const uploadHandleChange = (newFiles) => {
    setErrorText("");
    setFiles(newFiles);
  };

  const onSubmit = () => {
    if (isEmpty(files)) {
      return setErrorText("selectFileToUpload");
    }
    const [file] = files;
    if (!isCloudReportExtensionSupported(file.name)) {
      return setErrorText("fileFormatNotSupported");
    }
    return onUpload(file);
  };

  return (
    <Grid container spacing={SPACING_6}>
      {canUpload ? (
        <Grid item xs={12}>
          <Upload
            errorText={errorText}
            setErrorText={setErrorText}
            handleChange={uploadHandleChange}
            acceptedFiles={[
              "application/gzip",
              "application/x-gzip",
              "application/zip",
              "application/x-zip-compressed",
              "",
              "text/csv",
              ".csv"
            ]}
          />
          <FormButtonsWrapper justifyContent="center">
            <ButtonLoader variant="outlined" color="primary" isLoading={isLoading} messageId="upload" onClick={onSubmit} />
          </FormButtonsWrapper>
        </Grid>
      ) : (
        <Grid item xs={12}>
          <Typography align="center" paragraph data-test-id="p_permissions">
            <FormattedMessage id="youDoNotHaveEnoughPermissions" />
          </Typography>
        </Grid>
      )}
    </Grid>
  );
};

UploadCloudReportData.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  onUpload: PropTypes.func.isRequired,
  sendState: PropTypes.string,
  cloudAccounts: PropTypes.array
};

export default UploadCloudReportData;
