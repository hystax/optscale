import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import { useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import EnvironmentPropertyNameInput from "components/EnvironmentPropertyNameInput";
import EnvironmentPropertyValueInput from "components/EnvironmentPropertyValueInput";
import IconButton from "components/IconButton";
import PropertyLayout from "components/PropertyLayout";
import { isEmpty as isEmptyArray } from "utils/arrays";

const CreateEnvironmentFormPropertiesField = ({ fieldName, propertyFieldNames }) => {
  const {
    register,
    control,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  const { fields, append, remove } = useFieldArray({
    control,
    name: fieldName
  });

  const { name: propertyNameFieldName, value: propertyValueFieldName } = propertyFieldNames;

  const emptyProperty = {
    [propertyNameFieldName]: "",
    [propertyValueFieldName]: ""
  };

  return (
    <div>
      {!isEmptyArray(fields) && (
        <>
          <FormLabel component="p">
            <FormattedMessage id="properties" />
          </FormLabel>
          {fields.map((item, index) => (
            <div
              key={item.id}
              style={{
                marginBottom: index === fields.length - 1 ? 0 : "0.5rem"
              }}
            >
              <PropertyLayout
                propertyName={
                  <EnvironmentPropertyNameInput
                    name={`${fieldName}.${index}.${propertyNameFieldName}`}
                    register={register}
                    error={!!errors[fieldName]?.[index]?.[propertyNameFieldName]}
                    helperText={
                      errors[fieldName]?.[index]?.[propertyNameFieldName] &&
                      errors[fieldName]?.[index]?.[propertyNameFieldName]?.message
                    }
                    validate={{
                      unique: (value, formValues) => {
                        const propertiesWithSameName = formValues[fieldName].filter(
                          ({ [propertyNameFieldName]: propertyName }) => propertyName === value
                        );
                        const isPropertyUnique = propertiesWithSameName.length === 1;

                        return isPropertyUnique || intl.formatMessage({ id: "propertyNamesShouldBeUnique" });
                      }
                    }}
                    dataTestId={`property_name_${index}`}
                  />
                }
                propertyValue={
                  <EnvironmentPropertyValueInput
                    name={`${fieldName}.${index}.${propertyValueFieldName}`}
                    register={register}
                    error={!!errors[fieldName]?.[index]?.[propertyValueFieldName]}
                    helperText={
                      errors[fieldName]?.[index]?.[propertyValueFieldName] &&
                      errors[fieldName]?.[index]?.[propertyValueFieldName]?.message
                    }
                    dataTestId={`property_value_${index}`}
                  />
                }
                iconButtons={
                  <IconButton
                    color="error"
                    icon={<DeleteOutlinedIcon />}
                    onClick={() => remove(index)}
                    tooltip={{
                      show: true,
                      value: <FormattedMessage id="delete" />
                    }}
                    dataTestId={`btn_delete_property_${index}`}
                  />
                }
              />
            </div>
          ))}
        </>
      )}
      <FormControl fullWidth>
        <Button
          dashedBorder
          startIcon={<AddOutlinedIcon />}
          messageId="addProperty"
          size="large"
          color="primary"
          onClick={() => append(emptyProperty)}
          dataTestId="btn_add_property"
        />
      </FormControl>
    </div>
  );
};

export default CreateEnvironmentFormPropertiesField;
