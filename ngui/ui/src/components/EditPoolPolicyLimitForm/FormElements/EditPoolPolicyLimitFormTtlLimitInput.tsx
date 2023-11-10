import { Typography } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { TTL_LIMIT_MAX } from "utils/constants";
import { isWholeNumber } from "utils/validation";

const EditPoolPolicyLimitFormTtlLimitInput = ({ name, defaultValue, margin, enableLabel }) => {
  const {
    formState: { errors },
    register
  } = useFormContext();
  const intl = useIntl();

  return (
    <Input
      type="number"
      dataTestId="input_ttl"
      defaultValue={defaultValue}
      required
      error={!!errors[name]}
      helperText={errors[name] && errors[name].message}
      margin={margin}
      label={enableLabel ? <FormattedMessage id="ttl" /> : undefined}
      inputProps={{ min: 0, max: 720 }}
      InputProps={{
        endAdornment: (
          <Typography variant="body2">
            <FormattedMessage id="hours" />
          </Typography>
        )
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
          value: TTL_LIMIT_MAX,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: TTL_LIMIT_MAX })
        },
        validate: {
          whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
        }
      })}
    />
  );
};

export default EditPoolPolicyLimitFormTtlLimitInput;
