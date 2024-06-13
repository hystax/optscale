import { useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.EXPORTED_DAYS;

const ExportedDaysField = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      label={intl.formatMessage({
        id: "exportedDays"
      })}
      required
      InputProps={{
        endAdornment: <QuestionMark messageId="exportedDaysDescription" dataTestId="qmark_exported_days" />
      }}
      isLoading={isLoading}
      min={0}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
      }}
    />
  );
};

export default ExportedDaysField;
