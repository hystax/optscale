import { InputAdornment } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MAX_INT_32 } from "utils/constants";
import { isWholeNumber } from "utils/validation";

const OrganizationConstraintFormExpenseLimitInput = ({ defaultValue, name, margin, enableLabel = false }) => {
  const {
    formState: { errors },
    register
  } = useFormContext();

  const intl = useIntl();

  const { currencySymbol } = useOrganizationInfo();

  return (
    <Input
      type="number"
      dataTestId="input_expense_limit"
      defaultValue={defaultValue}
      required
      error={!!errors[name]}
      helperText={errors[name] && errors[name].message}
      margin={margin}
      label={enableLabel ? <FormattedMessage id="expenseLimit" /> : undefined}
      inputProps={{ min: 0 }}
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
      }}
      {...register(name, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        min: {
          value: 0,
          message: intl.formatMessage({ id: "moreOrEqual" }, { min: 0 })
        },
        max: {
          value: MAX_INT_32,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
        },
        validate: {
          whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
        }
      })}
    />
  );
};

export default OrganizationConstraintFormExpenseLimitInput;
