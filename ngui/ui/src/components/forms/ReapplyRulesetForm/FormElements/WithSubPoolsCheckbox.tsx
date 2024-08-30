import { FormattedMessage } from "react-intl";
import { Checkbox } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.INCLUDE_CHILDREN;

const WithSubPoolsCheckbox = () => <Checkbox name={FIELD_NAME} label={<FormattedMessage id="withSubPools" />} />;

export default WithSubPoolsCheckbox;
