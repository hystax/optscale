import { InputAdornment } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MAX_INT_32 } from "utils/constants";
import { isPositiveNumberOrZero } from "utils/validation";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TOTAL_BUDGET;

const TotalBudgetInput = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const { currencySymbol } = useOrganizationInfo();

  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="totalBudget" />}
      required
      dataTestId={`input_${FIELD_NAME}`}
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME]?.message}
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        validate: {
          positiveNumber: (value) =>
            isPositiveNumberOrZero(value) && value > 0 ? true : intl.formatMessage({ id: "positiveNumber" })
        },
        max: {
          value: MAX_INT_32,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
        }
      })}
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
      }}
    />
  );
};

export default TotalBudgetInput;
