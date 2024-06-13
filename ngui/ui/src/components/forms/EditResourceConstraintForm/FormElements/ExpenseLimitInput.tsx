import InputAdornment from "@mui/material/InputAdornment";
import { useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isWholeNumber } from "utils/validation";

const ExpenseLimitInput = ({ name, defaultValue, dataTestId }) => {
  const intl = useIntl();

  const { currencySymbol } = useOrganizationInfo();

  return (
    <NumberInput
      name={name}
      margin="none"
      dataTestId={dataTestId}
      required
      defaultValue={defaultValue}
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
