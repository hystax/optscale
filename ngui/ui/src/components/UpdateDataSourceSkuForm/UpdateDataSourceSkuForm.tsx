import { FormControl } from "@mui/material";
import InputAdornment from "@mui/material/InputAdornment";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { MAX_INT_32 } from "utils/constants";
import { isPositiveNumberOrZero } from "utils/validation";

const FIELD_NAME = "cost";

const UpdateDataSourceSkuForm = ({ sku, cost, onSubmit, onCancel, isLoading = false }) => {
  const { currencySymbol } = useOrganizationInfo();

  const methods = useForm({
    defaultValues: {
      cost
    }
  });

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = methods;

  return (
    <FormProvider {...methods}>
      <FormControl>
        <KeyValueLabel keyMessageId="sku" value={sku} />
      </FormControl>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Input
          required
          dataTestId="input_cost"
          error={!!errors[FIELD_NAME]}
          helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
          label={<FormattedMessage id="cost" />}
          {...register(FIELD_NAME, {
            valueAsNumber: true,
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            },
            validate: {
              isPositiveNumberOrZero
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
        <FormButtonsWrapper>
          <ButtonLoader
            dataTestId="btn_update_data_source_sku"
            loaderDataTestId="loading_btn_update_data_source_sku"
            messageId="save"
            color="primary"
            variant="contained"
            type="submit"
            isLoading={isLoading}
          />
          <Button dataTestId="btn_cancel_update_data_source_sku" messageId="cancel" onClick={onCancel} />
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export default UpdateDataSourceSkuForm;
