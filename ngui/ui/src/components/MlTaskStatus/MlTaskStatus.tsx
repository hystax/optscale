import { FormattedMessage } from "react-intl";
import MlRunStatus from "components/MlRunStatus";
import { ML_TASK_STATUS } from "utils/constants";

const MlTaskStatus = ({ status, iconSize }) =>
  status === ML_TASK_STATUS.CREATED ? <FormattedMessage id="created" /> : <MlRunStatus status={status} iconSize={iconSize} />;

export default MlTaskStatus;
