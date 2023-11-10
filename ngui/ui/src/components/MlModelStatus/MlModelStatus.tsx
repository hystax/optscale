import { FormattedMessage } from "react-intl";
import MlRunStatus from "components/MlRunStatus";
import { ML_MODEL_STATUS } from "utils/constants";

const MlModelStatus = ({ status, iconSize }) =>
  status === ML_MODEL_STATUS.CREATED ? <FormattedMessage id="created" /> : <MlRunStatus status={status} iconSize={iconSize} />;

export default MlModelStatus;
