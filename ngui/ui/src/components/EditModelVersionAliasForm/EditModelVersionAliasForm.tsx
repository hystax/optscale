import { FormProvider, useForm } from "react-hook-form";
import { Buttons, AliasesField, FIELD_NAMES, isAliasValid } from "./FormElements";
import { EditModelVersionAliasFormProps, FormValues } from "./types";

const EditModelVersionAliasForm = ({
  modelVersion,
  aliasToVersionMap,
  onSubmit,
  onCancel,
  isLoadingProps
}: EditModelVersionAliasFormProps) => {
  const { isSubmitLoading } = isLoadingProps;

  const methods = useForm<FormValues>({
    defaultValues: {
      [FIELD_NAMES.ALIASES_FIELD_NAME]: modelVersion.aliases ?? []
    }
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        data-test-id="version_alias_form"
        onSubmit={handleSubmit((formData) => {
          onSubmit({
            ...formData,
            aliases: formData.aliases.filter(isAliasValid)
          });
        })}
        noValidate
      >
        <AliasesField modelVersion={modelVersion} aliasToVersionMap={aliasToVersionMap} />
        <Buttons onCancel={onCancel} isLoading={isSubmitLoading} />
      </form>
    </FormProvider>
  );
};

export default EditModelVersionAliasForm;
