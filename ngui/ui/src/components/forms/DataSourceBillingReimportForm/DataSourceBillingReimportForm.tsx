import { FormProvider, useForm } from "react-hook-form";
import FormContentDescription from "components/FormContentDescription";
import { FormButtons, ReimportFromDatePicker } from "./FormElements";
import { DataSourceBillingReimportFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const DataSourceBillingReimportForm = ({ onSubmit, isSubmitLoading = false }: DataSourceBillingReimportFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues(),
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <ReimportFromDatePicker />
        <FormContentDescription
          alertProps={{
            messageId: "billingReimportWarning",
            severity: "warning",
          }}
        />
        <FormButtons isLoading={isSubmitLoading} />
      </form>
    </FormProvider>
  );
};

export default DataSourceBillingReimportForm;
