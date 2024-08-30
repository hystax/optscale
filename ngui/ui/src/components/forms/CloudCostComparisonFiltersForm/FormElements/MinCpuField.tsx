import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.MIN_CPU;

const MinCpuField = () => {
  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      label={<FormattedMessage id="minCpu" />}
      required
      min={0}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
      }}
    />
  );
};

export default MinCpuField;
