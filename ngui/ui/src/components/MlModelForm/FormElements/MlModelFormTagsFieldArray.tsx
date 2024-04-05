import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box, FormControl, FormLabel } from "@mui/material";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import IconButton from "components/IconButton";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { notOnlyWhiteSpaces } from "utils/validation";

export const ARRAY_FIELD_NAME = "tags";
export const KEY_FIELD_NAME = "key";
export const VALUE_FIELD_NAME = "value";

const KeyInput = ({ index }: { index: number }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="name" />}
      required
      error={!!errors[ARRAY_FIELD_NAME]?.[index]?.[KEY_FIELD_NAME]}
      helperText={
        errors[ARRAY_FIELD_NAME]?.[index]?.[KEY_FIELD_NAME] && errors[ARRAY_FIELD_NAME]?.[index]?.[KEY_FIELD_NAME]?.message
      }
      {...register(`${ARRAY_FIELD_NAME}.${index}.${KEY_FIELD_NAME}`, {
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
            const tagsWithSameKey = formValues[ARRAY_FIELD_NAME].filter(({ [KEY_FIELD_NAME]: key }) => key === value);

            const isPropertyUnique = tagsWithSameKey.length === 1;

            return isPropertyUnique || intl.formatMessage({ id: "thisFieldShouldBeUnique" });
          },
          notOnlyWhiteSpaces
        }
      })}
      dataTestId={`tag_name_${index}`}
    />
  );
};

const ValueInput = ({ index }: { index: number }) => {
  const {
    formState: { errors },
    control
  } = useFormContext();

  const intl = useIntl();

  const fieldName = `${ARRAY_FIELD_NAME}.${index}.${VALUE_FIELD_NAME}`;

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
              inputName: intl.formatMessage({ id: "value" }),
              max: DEFAULT_MAX_INPUT_LENGTH
            }
          )
        },
        validate: {
          notOnlyWhiteSpaces
        }
      }}
      render={({ field }) => (
        <Input
          label={<FormattedMessage id="value" />}
          required
          error={!!errors[ARRAY_FIELD_NAME]?.[index]?.[VALUE_FIELD_NAME]}
          helperText={
            errors[ARRAY_FIELD_NAME]?.[index]?.[VALUE_FIELD_NAME] &&
            errors[ARRAY_FIELD_NAME]?.[index]?.[VALUE_FIELD_NAME]?.message
          }
          dataTestId={`tag_value_${index}`}
          {...field}
        />
      )}
    />
  );
};

const MlModelFormTagsFieldArray = ({ name = ARRAY_FIELD_NAME, isLoading = false }) => {
  const { control } = useFormContext();

  const { fields, append, remove } = useFieldArray({
    control,
    name
  });

  const onAppend = () =>
    append({
      [KEY_FIELD_NAME]: "",
      [VALUE_FIELD_NAME]: ""
    });

  return (
    <>
      <FormLabel component="p">
        <FormattedMessage id="tags" />
      </FormLabel>
      {isLoading ? (
        <InputLoader fullWidth />
      ) : (
        <>
          {fields.map((item, index) => (
            <Box key={item.id} display="flex" gap={SPACING_1} flexWrap="wrap">
              <Box flexGrow={1} flexBasis="150px">
                <KeyInput index={index} />
              </Box>
              <Box display="flex" flexBasis="200px" flexGrow={2} gap={SPACING_1}>
                <Box flexGrow={1}>
                  <ValueInput index={index} />
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
              messageId="addTag"
              size="large"
              color="primary"
              onClick={onAppend}
              dataTestId="btn_add_tag"
            />
          </FormControl>
        </>
      )}
    </>
  );
};

export default MlModelFormTagsFieldArray;
