import { FormattedMessage } from "react-intl";
import { Checkbox } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.REQUIRE_SSH_KEY;

const SshRequiredField = () => <Checkbox name={FIELD_NAME} label={<FormattedMessage id="requireSshKey" />} />;

export default SshRequiredField;
