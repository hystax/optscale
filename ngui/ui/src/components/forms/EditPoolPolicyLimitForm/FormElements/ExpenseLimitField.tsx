import { InputAdornment } from "@mui/material";
import { useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.LIMIT;

const ExpenseLimitField = () => {
  const intl = useIntl();

  const { currencySymbol } = useOrganizationInfo();

  return (
    <NumberInput
      name={FIELD_NAME}
      required
      inputProps={{ min: 0 }}
      min={0}
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
      }}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
      }}
      margin="none"
      dataTestId="input_expense_limit"
    />
  );
};

export default ExpenseLimitField;
