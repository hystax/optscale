import { FormProvider, useForm } from "react-hook-form";
import { FormButtons, NameField } from "./FormElements";
import { FormValues, RenameMlRunChartFormProps } from "./types";
import { getDefaultValues } from "./utils";

const RenameMlRunChartForm = ({ chartName, onRename }: RenameMlRunChartFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      name: chartName
    })
  });

  const { handleSubmit } = methods;

  const onSubmit = handleSubmit((formData) => {
    onRename(formData.name);
  });

  return (
    <FormProvider {...methods}>
      <form onSubmit={onSubmit} noValidate>
        <NameField />
        <FormButtons />
      </form>
    </FormProvider>
  );
};

export default RenameMlRunChartForm;
