import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { isPositiveNumberOrZero } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.TARGET_VALUE;

const TargetValueField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      label={<FormattedMessage id="targetValue" />}
      required
      valueAsNumber
      min={0}
      isLoading={isLoading}
      validate={{
        positiveNumber: (value) => (isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumber" }))
      }}
      dataTestId="input_name"
    />
  );
};

export default TargetValueField;
