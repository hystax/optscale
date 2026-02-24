import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

export const FIELD_NAME = FIELD_NAMES.MAXIMUM_RUNSET_RUNNERS;

const MaximumRunsetRunners = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      dataTestId="input_maximum_runset_runners"
      label={<FormattedMessage id="maximumRunsetRunners" />}
      required
      min={1}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true),
      }}
      isLoading={isLoading}
    />
  );
};

export default MaximumRunsetRunners;
