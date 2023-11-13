import { InputAdornment } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MAX_INT_32 } from "utils/constants";
import { isWholeNumber } from "utils/validation";

export const FIELD_NAME = "budget";

const MaximumRunsetBudgetField = ({ isLoading }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  const { currencySymbol } = useOrganizationInfo();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Input
      dataTestId="input_maximum_runset_budget"
      label={<FormattedMessage id="maximumRunsetBudget" />}
      required
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      {...register(FIELD_NAME, {
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
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
      }}
    />
  );
};

export default MaximumRunsetBudgetField;
