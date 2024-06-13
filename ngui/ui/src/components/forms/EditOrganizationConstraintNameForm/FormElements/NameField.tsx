import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.NAME;

const NameField = () => (
  <TextInput
    name={FIELD_NAME}
    label={<FormattedMessage id="name" />}
    required
    dataTestId={`input_${FIELD_NAME}`}
    sx={{
      marginRight: (theme) => theme.spacing(1)
    }}
  />
);

export default NameField;
