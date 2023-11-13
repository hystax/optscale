import InputAdornment from "@mui/material/InputAdornment";
import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Input from "components/Input";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MAX_INT_32 } from "utils/constants";
import { isWholeNumber } from "utils/validation";

const EditResourceConstraintFormExpenseLimitInput = ({ name, defaultValue, dataTestId }) => {
  const intl = useIntl();
  const {
    register,
    formState: { errors }
  } = useFormContext();
  const { currencySymbol } = useOrganizationInfo();

  return (
    <Input
      margin="none"
      type="number"
      dataTestId={dataTestId}
      required
      error={!!errors[name]}
      helperText={errors[name]?.message}
      defaultValue={defaultValue}
      inputProps={{
        min: 0
      }}
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

export default EditResourceConstraintFormExpenseLimitInput;
