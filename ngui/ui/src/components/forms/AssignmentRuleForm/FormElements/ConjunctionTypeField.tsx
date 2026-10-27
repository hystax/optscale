import { FormattedMessage } from "react-intl";
import { RadioGroup } from "components/forms/common/fields";
import { ASSIGNMENT_RULE_OPERATORS } from "utils/constants";
import { FIELD_NAMES } from "../utils";

const ConjunctionTypeField = ({ name = FIELD_NAMES.OPERATOR, isLoading = false }) => (
  <RadioGroup
    name={name}
    defaultValue={ASSIGNMENT_RULE_OPERATORS.AND}
    margin="none"
    row
    radioButtons={[
      {
        value: ASSIGNMENT_RULE_OPERATORS.AND,
        label: <FormattedMessage id="conjunctionTypes.and" />,
        isLoading: isLoading,
      },
      {
        value: ASSIGNMENT_RULE_OPERATORS.OR,
        label: <FormattedMessage id="conjunctionTypes.or" />,
        isLoading: isLoading,
      },
    ]}
  />
);

export default ConjunctionTypeField;
