import { FormattedMessage } from "react-intl";
import { Checkbox } from "components/forms/common/fields";
import { FIELD_NAMES } from "../utils";

const ActiveCheckboxField = ({ name = FIELD_NAMES.ACTIVE, isLoading = false }) => (
  <Checkbox name={name} label={<FormattedMessage id="active" />} isLoading={isLoading} />
);

export default ActiveCheckboxField;
