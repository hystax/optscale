import { useDispatch } from "react-redux";
import { uploadCloudReport } from "api";
import { UPLOAD_CLOUD_REPORT } from "api/restapi/actionTypes";
import UploadCloudReportData from "components/UploadCloudReportData";
import { useApiState } from "hooks/useApiState";

type UploadCloudReportDataContainerProps = {
  cloudAccountId: string;
  dataSourceType: string;
};

const UploadCloudReportDataContainer = ({ cloudAccountId, dataSourceType }: UploadCloudReportDataContainerProps) => {
  const dispatch = useDispatch();

  const { isLoading: isUploadLoading } = useApiState(UPLOAD_CLOUD_REPORT);

  const onUpload = (file: File) => {
    dispatch(uploadCloudReport(cloudAccountId, file));
  };

  return <UploadCloudReportData dataSourceType={dataSourceType} onUpload={onUpload} isLoading={isUploadLoading} />;
};

export default UploadCloudReportDataContainer;
