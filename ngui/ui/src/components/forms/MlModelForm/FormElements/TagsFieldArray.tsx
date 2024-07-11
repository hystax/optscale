import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box, FormControl, FormLabel } from "@mui/material";
import { useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import { TextInput } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import InputLoader from "components/InputLoader";
import { SPACING_1 } from "utils/layouts";
import { notOnlyWhiteSpaces } from "utils/validation";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const { FIELD_NAME } = FIELD_NAMES.TAGS_FIELD_ARRAY;
const KEY_FIELD_NAME = FIELD_NAMES.TAGS_FIELD_ARRAY.KEY;
const VALUE_FIELD_NAME = FIELD_NAMES.TAGS_FIELD_ARRAY.VALUE;

const KeyInput = ({ index }: { index: number }) => {
  const intl = useIntl();

  return (
    <TextInput
      label={<FormattedMessage id="name" />}
      name={`${FIELD_NAME}.${index}.${KEY_FIELD_NAME}`}
      required
      dataTestId={`tag_name_${index}`}
      validate={{
        unique: (value, formValues) => {
          const tagsWithSameKey = formValues[FIELD_NAME].filter(({ [KEY_FIELD_NAME]: key }) => key === value);

          const isPropertyUnique = tagsWithSameKey.length === 1;

          return isPropertyUnique || intl.formatMessage({ id: "thisFieldMustBeUnique" });
        },
        notOnlyWhiteSpaces
      }}
    />
  );
};

const ValueInput = ({ index }: { index: number }) => {
  const fieldName = `${FIELD_NAME}.${index}.${VALUE_FIELD_NAME}`;

  return <TextInput name={fieldName} label={<FormattedMessage id="value" />} required dataTestId={`tag_value_${index}`} />;
};

const FieldArray = () => {
  const { control } = useFormContext<FormValues>();

  const { fields, append, remove } = useFieldArray<FormValues>({
    control,
    name: FIELD_NAME
  });

  const onAppend = () =>
    append({
      [KEY_FIELD_NAME]: "",
      [VALUE_FIELD_NAME]: ""
    });

  return (
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
  );
};

const TagsFieldArray = ({ isLoading = false }) => (
  <>
    <FormLabel component="p">
      <FormattedMessage id="tags" />
    </FormLabel>
    {isLoading ? <InputLoader fullWidth /> : <FieldArray />}
  </>
);

export default TagsFieldArray;
