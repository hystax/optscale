import { useDispatch } from "react-redux";
import { uploadCloudReport } from "api";
import { UPLOAD_CLOUD_REPORT } from "api/restapi/actionTypes";
import UploadCloudReportData from "components/UploadCloudReportData";
import { useApiState } from "hooks/useApiState";

const UploadCloudReportDataContainer = ({ cloudAccountId }) => {
  const dispatch = useDispatch();

  const { isLoading: isUploadLoading } = useApiState(UPLOAD_CLOUD_REPORT);

  const onUpload = (file) => {
    dispatch(uploadCloudReport(cloudAccountId, file));
  };

  return <UploadCloudReportData onUpload={onUpload} isLoading={isUploadLoading} />;
};

export default UploadCloudReportDataContainer;
