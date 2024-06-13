import { FormControl } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { CostField } from "./FormElements";
import { FormValues, UpdateDataSourceSkuFormProps } from "./type";
import { getDefaultValues } from "./utils";

const UpdateDataSourceSkuForm = ({ sku, cost, onSubmit, onCancel, isLoading = false }: UpdateDataSourceSkuFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({ cost })
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <FormControl>
          <KeyValueLabel keyMessageId="sku" value={sku} />
        </FormControl>
        <CostField />
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
