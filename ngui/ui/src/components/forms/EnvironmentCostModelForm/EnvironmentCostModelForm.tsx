import { FormProvider, useForm } from "react-hook-form";
import { FormButtons, HourlyPriceField } from "./FormElements";
import { EnvironmentCostModelFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const EnvironmentCostModelForm = ({
  defaultHourlyPrice,
  onSubmit,
  onCancel,
  isLoading = false
}: EnvironmentCostModelFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      hourlyPrice: defaultHourlyPrice
    })
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <HourlyPriceField />
        <FormButtons isLoading={isLoading} onCancel={onCancel} />
      </form>
    </FormProvider>
  );
};

export default EnvironmentCostModelForm;
