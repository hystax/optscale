import React from "react";
import AttachFileOutlinedIcon from "@mui/icons-material/AttachFileOutlined";
import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import FormHelperText from "@mui/material/FormHelperText";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import useStyles from "./Dropzone.styles";
import useDropzone from "./useDropzone";

const Dropzone = ({ errorMessageId, onChange, messageId = "dropOrSelectFile", acceptedFiles, multiple = false }) => {
  const { classes, cx } = useStyles();
  const accept = acceptedFiles.join(",");

  const { fileInputRef, file, highlight, onFilesAdded, onFilesRemoved, openFileDialog, onDragOver, onDragLeave, onDrop } =
    useDropzone({ onChange });

  return (
    <>
      <div
        className={cx(
          classes.dropzone,
          classes.content,
          highlight ? classes.highlight : "",
          errorMessageId ? classes.error : ""
        )}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={openFileDialog}
      >
        <CloudUploadOutlinedIcon fontSize="large" color={errorMessageId ? "error" : "primary"} />
        <Typography>
          <FormattedMessage id={messageId} />
        </Typography>
        {file !== null && (
          <div className={classes.content}>
            <AttachFileOutlinedIcon />
            <Typography>
              <strong>{file.name}</strong>
            </Typography>
            <IconButton icon={<DeleteOutlinedIcon color="error" />} onClick={(event) => onFilesRemoved(event)} />
          </div>
        )}
        <input
          ref={fileInputRef}
          accept={accept}
          multiple={multiple}
          hidden
          type="file"
          onChange={({ target: { files } }) => onFilesAdded(files)}
        />
      </div>
      {errorMessageId && (
        <FormHelperText error>
          <FormattedMessage id={errorMessageId} />
        </FormHelperText>
      )}
    </>
  );
};

Dropzone.propTypes = {
  errorMessageId: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  messageId: PropTypes.string,
  acceptedFiles: PropTypes.array,
  multiple: PropTypes.bool
};

export default Dropzone;
