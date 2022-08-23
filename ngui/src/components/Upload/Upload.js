import React from "react";
import FormHelperText from "@mui/material/FormHelperText";
import PropTypes from "prop-types";
import { useIntl, FormattedMessage } from "react-intl";
import { DropzoneArea } from "react-mui-dropzone";
import { MB } from "utils/constants";
import useStyles from "./Upload.styles";

// TODO: move back to original component
// Please note, that https://www.npmjs.com/package/material-ui-dropzone was
// replaced with https://www.npmjs.com/package/react-mui-dropzone
// Probably we should move back, after it will get "official" support for mui v5

const Upload = ({ acceptedFiles, handleChange, setErrorText, errorText, filesLimit = 1, maxFileSize = 512 }) => {
  const intl = useIntl();
  const { classes } = useStyles();

  return (
    <>
      <DropzoneArea
        showAlerts={false}
        filesLimit={filesLimit}
        maxFileSize={maxFileSize * MB}
        acceptedFiles={acceptedFiles}
        dropzoneClass={classes.dropZone}
        dropzoneParagraphClass={classes.title}
        showFileNames
        dropzoneText={intl.formatMessage({ id: "uploadText" })}
        onChange={handleChange}
        getDropRejectMessage={(rejected, accepted, maxSize) => {
          if (rejected.size > maxSize) {
            return "fileIsTooBig";
          }
          if (!acceptedFiles.includes(rejected.type)) {
            return "fileTypeNotSupported";
          }
          return "fileWasRejected";
        }}
        getFileLimitExceedMessage={() => "numberOfFilesExceeded"}
        onAlert={(message, type) => {
          if (type === "error") {
            setErrorText(message);
          }
        }}
      />
      {errorText && (
        <FormHelperText error>
          <FormattedMessage id={errorText} />
        </FormHelperText>
      )}
    </>
  );
};

Upload.propTypes = {
  acceptedFiles: PropTypes.array.isRequired,
  handleChange: PropTypes.func.isRequired,
  setErrorText: PropTypes.func.isRequired,
  errorText: PropTypes.string,
  filesLimit: PropTypes.number,
  maxFileSize: PropTypes.number
};

export default Upload;
