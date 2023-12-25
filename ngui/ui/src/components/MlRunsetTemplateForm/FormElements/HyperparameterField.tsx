import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import IconButton from "components/IconButton";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { doNotBeginWithNumber, isRunsetTemplateEnvironmentVariable } from "utils/validation";

export const ARRAY_FIELD_NAME = "parameters";
export const NAME_FIELD_NAME = "parameterName";
export const ENVIRONMENT_VARIABLE_FIELD = "environmentVariable";

const NameInput = ({ index }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="name" />}
      required
      error={!!errors[ARRAY_FIELD_NAME]?.[index]?.[NAME_FIELD_NAME]}
      helperText={
        errors[ARRAY_FIELD_NAME]?.[index]?.[NAME_FIELD_NAME] && errors[ARRAY_FIELD_NAME]?.[index]?.[NAME_FIELD_NAME]?.message
      }
      {...register(`${ARRAY_FIELD_NAME}.${index}.${NAME_FIELD_NAME}`, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            {
              inputName: intl.formatMessage({ id: "name" }),
              max: DEFAULT_MAX_INPUT_LENGTH
            }
          )
        },
        validate: {
          unique: (value, formValues) => {
            const propertiesWithSameName = formValues[ARRAY_FIELD_NAME].filter(
              ({ [NAME_FIELD_NAME]: propertyName }) => propertyName === value
            );

            const isPropertyUnique = propertiesWithSameName.length === 1;

            return isPropertyUnique || intl.formatMessage({ id: "thisFieldShouldBeUnique" });
          }
        }
      })}
      dataTestId={`hyperparameter_name_${index}`}
    />
  );
};

const EnvironmentName = ({ index }) => {
  const {
    formState: { errors },
    control
  } = useFormContext();

  const intl = useIntl();

  const fieldName = `${ARRAY_FIELD_NAME}.${index}.${ENVIRONMENT_VARIABLE_FIELD}`;

  return (
    <Controller
      name={fieldName}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            {
              inputName: intl.formatMessage({ id: "environmentVariable" }),
              max: DEFAULT_MAX_INPUT_LENGTH
            }
          )
        },
        validate: {
          unique: (value, formValues) => {
            const propertiesWithSameName = formValues[ARRAY_FIELD_NAME].filter(
              ({ [ENVIRONMENT_VARIABLE_FIELD]: propertyValue }) => propertyValue === value
            );
            const isPropertyUnique = propertiesWithSameName.length === 1;

            return isPropertyUnique || intl.formatMessage({ id: "thisFieldShouldBeUnique" });
          },
          isRunsetTemplateEnvironmentVariable: (value) =>
            isRunsetTemplateEnvironmentVariable(intl.formatMessage({ id: "environmentVariable" }))(value),
          doNotBeginWithNumber: doNotBeginWithNumber(intl.formatMessage({ id: "environmentVariable" }))
        }
      }}
      render={({ field: { onChange, ...rest } }) => (
        <Input
          label={<FormattedMessage id="environmentVariable" />}
          required
          error={!!errors[ARRAY_FIELD_NAME]?.[index]?.[ENVIRONMENT_VARIABLE_FIELD]}
          helperText={
            errors[ARRAY_FIELD_NAME]?.[index]?.[ENVIRONMENT_VARIABLE_FIELD] &&
            errors[ARRAY_FIELD_NAME]?.[index]?.[ENVIRONMENT_VARIABLE_FIELD]?.message
          }
          dataTestId={`hyperparameter_environment_name_${index}`}
          onChange={(e) => onChange(e.target.value.toLocaleUpperCase())}
          {...rest}
        />
      )}
    />
  );
};

const HyperparameterField = ({ isLoading }) => {
  const { control } = useFormContext();

  const { fields, append, remove } = useFieldArray({
    control,
    name: ARRAY_FIELD_NAME
  });

  const onAppend = () =>
    append({
      [NAME_FIELD_NAME]: "",
      [ENVIRONMENT_VARIABLE_FIELD]: ""
    });

  return (
    <>
      <FormLabel component="p">
        <FormattedMessage id="hyperparameters" />
      </FormLabel>
      {isLoading ? (
        <InputLoader fullWidth />
      ) : (
        <>
          {fields.map((item, index) => (
            <Box key={item.id} display="flex" gap={SPACING_1} flexWrap="wrap">
              <Box flexGrow={1} flexBasis="150px">
                <NameInput index={index} />
              </Box>
              <Box display="flex" flexBasis="200px" flexGrow={2} gap={SPACING_1}>
                <Box flexGrow={1}>
                  <EnvironmentName index={index} />
                </Box>
                <Box>
                  <FormControl sx={{ alignItems: "flex-end", width: "100%" }}>
                    <IconButton
                      color="error"
                      icon={<DeleteOutlinedIcon />}
                      onClick={() => remove(index)}
                      tooltip={{
                        show: true,
                        value: <FormattedMessage id="delete" />
                      }}
                      dataTestId={`btn_delete_hyperparameter_${index}`}
                    />
                  </FormControl>
                </Box>
              </Box>
            </Box>
          ))}
          <FormControl fullWidth>
            <Button
              dashedBorder
              startIcon={<AddOutlinedIcon />}
              messageId="addHyperparameter"
              size="large"
              color="primary"
              onClick={onAppend}
              dataTestId="btn_add_hyperparameter"
            />
          </FormControl>
        </>
      )}
    </>
  );
};

export default HyperparameterField;
