import { FormProvider, type SubmitHandler, useForm } from "react-hook-form";
import { FIELD_NAMES } from "./constants";
import { FormButtons, NameField } from "./FormElements";
import { CreateColumnSetFormProps, FormValues } from "./types";

const CreateColumnSetForm = ({ onSubmit, isLoadingProps = {} }: CreateColumnSetFormProps) => {
  const { isSubmitLoading } = isLoadingProps;

  const methods = useForm<FormValues>();

  const { reset, handleSubmit } = methods;

  const onFormSubmit: SubmitHandler<FormValues> = (formData) => onSubmit(formData[FIELD_NAMES.NAME]).then(() => reset());

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onFormSubmit)} noValidate>
        <NameField />
        <FormButtons isLoading={isSubmitLoading} />
      </form>
    </FormProvider>
  );
};

export default CreateColumnSetForm;
