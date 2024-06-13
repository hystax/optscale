import InputAdornment from "@mui/material/InputAdornment";
import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.LIMIT;

const ExpenseLimitInput = () => {
  const intl = useIntl();

  const { currencySymbol } = useOrganizationInfo();

  return (
    <NumberInput
      name={FIELD_NAME}
      required
      label={<FormattedMessage id="expenseLimit" />}
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
      }}
      min={0}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
      }}
    />
  );
};

export default ExpenseLimitInput;
