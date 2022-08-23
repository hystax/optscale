import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { UPLOAD_CODE_REPORT } from "api/restapi/actionTypes";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import TechnicalAuditService from "services/TechnicalAuditService";
import { isError } from "utils/api";
import SourceCodeStateReport from "./SourceCodeStateReport";

const SourceCodeStateReportContainer = ({ isConfirmed, onUploadCallback, onConfirm, isLoadingProps = {} }) => {
  const dispatch = useDispatch();

  const { useUploadCodeReport } = TechnicalAuditService();
  const { upload, isUploadCodeReportLoading, uploadStatus } = useUploadCodeReport();

  const { useGetTechnicalAudit } = OrganizationOptionsService();
  const {
    options: { codeReportFiles = [] }
  } = useGetTechnicalAudit();

  const onUpload = (file) =>
    dispatch((_, getState) => {
      upload(file).then(() => {
        if (!isError(UPLOAD_CODE_REPORT, getState())) {
          onUploadCallback({ codeReportFiles: [file.name] });
        }
      });
    });

  return (
    <SourceCodeStateReport
      onUpload={onUpload}
      onUploadCallback={onUploadCallback}
      uploadStatus={uploadStatus}
      isLoadingProps={{ ...isLoadingProps, isUploadCodeReportLoading }}
      onConfirm={onConfirm}
      isConfirmed={isConfirmed}
      alreadyUploadedFilesCount={codeReportFiles.length}
    />
  );
};

SourceCodeStateReportContainer.propTypes = {
  isConfirmed: PropTypes.bool.isRequired,
  onConfirm: PropTypes.func.isRequired,
  onUploadCallback: PropTypes.func.isRequired,
  isLoadingProps: PropTypes.object
};

export default SourceCodeStateReportContainer;
