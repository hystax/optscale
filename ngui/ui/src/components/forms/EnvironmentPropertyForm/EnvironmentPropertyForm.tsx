import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import { FormProvider, useForm } from "react-hook-form";
import IconButton from "components/IconButton";
import PropertyLayout from "components/PropertyLayout";
import { PropertyNameField, PropertyValueField } from "./FormElements";
import { EnvironmentPropertyFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const EnvironmentPropertyForm = ({
  defaultPropertyName,
  defaultPropertyValue,
  onSubmit,
  onCancel,
  existingProperties,
  isLoading = false,
  isEdit = false
}: EnvironmentPropertyFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      propertyName: defaultPropertyName,
      propertyValue: defaultPropertyValue
    })
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <PropertyLayout
          propertyName={
            <PropertyNameField
              readOnly={isEdit}
              defaultPropertyName={defaultPropertyName}
              existingProperties={existingProperties}
            />
          }
          propertyValue={<PropertyValueField />}
          iconButtons={
            <>
              <IconButton icon={<CheckOutlinedIcon />} type="submit" isLoading={isLoading} />
              <IconButton icon={<CloseIcon />} onClick={onCancel} />
            </>
          }
        />
      </form>
    </FormProvider>
  );
};

export default EnvironmentPropertyForm;
