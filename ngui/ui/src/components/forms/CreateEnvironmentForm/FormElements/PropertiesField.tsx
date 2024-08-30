import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import { useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import { TextInput } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import PropertyLayout from "components/PropertyLayout";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { DEFAULT_MAX_TEXTAREA_LENGTH, ENVIRONMENT_PROPERTY_NAME_MAX_INPUT_LENGTH } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const { FIELD_NAME, PROPERTY_NAME, PROPERTY_VALUE } = FIELD_NAMES.PROPERTIES_FIELD_ARRAY;

const emptyProperty = {
  [PROPERTY_NAME]: "",
  [PROPERTY_VALUE]: ""
};

const PropertiesField = () => {
  const { control } = useFormContext();

  const intl = useIntl();

  const { fields, append, remove } = useFieldArray({
    control,
    name: FIELD_NAME
  });

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
                  <TextInput
                    name={`${FIELD_NAME}.${index}.${PROPERTY_NAME}`}
                    label={<FormattedMessage id="name" />}
                    required
                    maxLength={ENVIRONMENT_PROPERTY_NAME_MAX_INPUT_LENGTH}
                    validate={{
                      unique: (value, formValues) => {
                        const propertiesWithSameName = formValues[FIELD_NAME].filter(
                          ({ [PROPERTY_NAME]: propertyName }) => propertyName === value
                        );
                        const isPropertyUnique = propertiesWithSameName.length === 1;

                        return isPropertyUnique || intl.formatMessage({ id: "propertyNamesMustBeUnique" });
                      }
                    }}
                    dataTestId={`property_name_${index}`}
                  />
                }
                propertyValue={
                  <TextInput
                    name={`${FIELD_NAME}.${index}.${PROPERTY_VALUE}`}
                    label={<FormattedMessage id="value" />}
                    required
                    maxLength={DEFAULT_MAX_TEXTAREA_LENGTH}
                    multiline
                    rows={4}
                    placeholder={intl.formatMessage({ id: "markdownIsSupported" })}
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

export default PropertiesField;
