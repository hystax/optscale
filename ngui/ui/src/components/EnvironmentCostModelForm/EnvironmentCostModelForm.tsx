import InputAdornment from "@mui/material/InputAdornment";
import { useForm } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MAX_INT_32 } from "utils/constants";
import { isPositiveNumberOrZero, costModelValueMaxFractionDigitsValidation } from "utils/validation";

const HOURLY_PRICE_INPUT_NAME = "hourlyPrice";

// TODO: We need to check the "number" type in the Mozilla firefox browser, for example. The value is not validated correctly and the string values show a error in the required field.
const EnvironmentCostModelForm = ({ onSubmit, defaultHourlyPrice, isLoading, onCancel }) => {
  const intl = useIntl();
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm({
    defaultValues: {
      [HOURLY_PRICE_INPUT_NAME]: defaultHourlyPrice || 0
    }
  });
  const { currencySymbol } = useOrganizationInfo();

  return (
    <form
      onSubmit={handleSubmit((data) => {
        onSubmit({
          [HOURLY_PRICE_INPUT_NAME]: Number(data[HOURLY_PRICE_INPUT_NAME])
        });
      })}
      noValidate
    >
      <Input
        required
        // type="number"
        error={!!errors[HOURLY_PRICE_INPUT_NAME]}
        helperText={errors[HOURLY_PRICE_INPUT_NAME] && errors[HOURLY_PRICE_INPUT_NAME].message}
        InputProps={{
          startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
        }}
        label={<FormattedMessage id="hourlyPrice" />}
        {...register(HOURLY_PRICE_INPUT_NAME, {
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
            positiveNumber: (value) => (isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumber" })),
            fractionDigits: costModelValueMaxFractionDigitsValidation
          }
        })}
        dataTestId="input_cpu"
      />
      <FormButtonsWrapper>
        <ButtonLoader
          isLoading={isLoading}
          variant="contained"
          color="primary"
          messageId="save"
          type="submit"
          loaderDataTestId="loading_btn_save"
          dataTestId="btn_save"
        />
        <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
      </FormButtonsWrapper>
    </form>
  );
};

export default EnvironmentCostModelForm;
