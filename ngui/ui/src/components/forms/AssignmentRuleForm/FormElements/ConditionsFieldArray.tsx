import { Fragment } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import { useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { makeStyles } from "tss-react/mui";
import Button from "components/Button";
import { Selector, TextInput } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import InputLoader from "components/InputLoader";
import { ItemContent, ItemContentWithDataSourceIcon } from "components/Selector";
import {
  CONDITION_TYPES,
  TAG_IS,
  CLOUD_IS,
  TAG_VALUE_STARTS_WITH,
  TAG_EXISTS,
  DEFAULT_CONDITION,
  ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH
} from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { FIELD_NAMES } from "../utils";

const { FIELD_NAME, TYPE, META_INFO } = FIELD_NAMES.CONDITIONS_FIELD_ARRAY;

const useStyles = makeStyles()((theme) => ({
  item: {
    width: "100%",
    minWidth: 0
  },
  keyValueInput: {
    width: `calc(50% - ${theme.spacing(SPACING_1 / 2)})`
  },
  spaceRight: {
    marginRight: theme.spacing(1)
  },
  deleteButton: {
    alignItems: "flex-end"
  }
}));

const ConditionsFieldArray = ({ name = FIELD_NAME, isLoading = false, cloudAccounts }) => {
  const { classes, cx } = useStyles();

  const { control, watch } = useFormContext();

  const { fields, append, remove } = useFieldArray({
    control,
    name
  });

  const watchConditions = watch(name);

  const renderInputField = (field, count, labelMessageId = "value") => (
    <TextInput
      name={`${name}.${count}.${META_INFO}`}
      className={classes.item}
      dataTestId={`input_${labelMessageId}_${count}`}
      defaultValue={field[META_INFO]}
      fullWidth={false}
      label={<FormattedMessage id={labelMessageId} />}
      required
    />
  );

  const renderKeyValueField = (field, count) => {
    const KEY_INPUT_NAME = FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TAG_KEY_FIELD_NAME;
    const VALUE_INPUT_NAME = FIELD_NAMES.CONDITIONS_FIELD_ARRAY.TAG_VALUE_FIELD_NAME;

    return (
      <Box className={classes.item}>
        <TextInput
          name={`${name}.${count}.${KEY_INPUT_NAME}`}
          defaultValue={field[KEY_INPUT_NAME]}
          fullWidth={false}
          label={<FormattedMessage id="key" />}
          dataTestId={`input_key_${count}`}
          required
          autoFocus={false}
          className={cx(classes.spaceRight, classes.keyValueInput)}
        />
        <TextInput
          name={`${name}.${count}.${VALUE_INPUT_NAME}`}
          defaultValue={field[VALUE_INPUT_NAME]}
          fullWidth={false}
          label={<FormattedMessage id="value" />}
          dataTestId={`input_value_${count}`}
          required
          autoFocus={false}
          className={classes.keyValueInput}
        />
      </Box>
    );
  };

  const renderCloudAccountSelector = (field, count) => {
    const NAME = FIELD_NAMES.CONDITIONS_FIELD_ARRAY.CLOUD_IS_FIELD_NAME;

    return (
      <Selector
        name={`${name}.${count}.${NAME}`}
        defaultValue={field[NAME] ?? ""}
        id={`selector-cloud-account-${count}`}
        fullWidth
        required
        labelMessageId="dataSource"
        items={cloudAccounts.map(({ id, name: cloudAccountName, type }) => ({
          value: id,
          content: <ItemContentWithDataSourceIcon dataSourceType={type}>{cloudAccountName}</ItemContentWithDataSourceIcon>
        }))}
      />
    );
  };

  const conditionRow = (field, count) => {
    const condition = watchConditions?.[count]?.[TYPE];

    const renderField = () => {
      switch (condition) {
        case TAG_IS:
        case TAG_VALUE_STARTS_WITH:
          return renderKeyValueField(field, count);
        case CLOUD_IS:
          return renderCloudAccountSelector(field, count);
        case TAG_EXISTS:
          return renderInputField(field, count, "key");
        default:
          return renderInputField(field, count);
      }
    };

    return (
      <Box display="flex" gap={SPACING_1} flexWrap="wrap">
        <Box flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM} flexGrow={1}>
          <Selector
            name={`${name}.${count}.${TYPE}`}
            defaultValue={field[TYPE]}
            id={`selector-type-${count}`}
            fullWidth
            required
            labelMessageId="type"
            items={Object.entries(CONDITION_TYPES).map(([conditionType, conditionMessageId]) => ({
              value: conditionType,
              content: (
                <ItemContent>
                  <FormattedMessage id={conditionMessageId} />
                </ItemContent>
              )
            }))}
          />
        </Box>
        <Box display="flex" flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM} flexGrow={2} gap={SPACING_1}>
          <Box flexGrow={1}>{renderField()}</Box>
          <Box>
            <FormControl>
              <IconButton
                color="error"
                icon={<DeleteOutlinedIcon />}
                onClick={() => (fields.length > 1 ? remove(count) : null)}
                tooltip={{
                  show: true,
                  value: <FormattedMessage id="delete" />
                }}
                dataTestId={`btn_delete_${count}`}
              />
            </FormControl>
          </Box>
        </Box>
      </Box>
    );
  };

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <>
      {fields.map((item, index) => (
        <Fragment key={item.id}>{conditionRow(item, index)}</Fragment>
      ))}
      <FormControl fullWidth>
        <Button
          dashedBorder
          startIcon={<AddOutlinedIcon />}
          messageId="add"
          dataTestId="btn_add"
          size="large"
          color="primary"
          onClick={() => append(DEFAULT_CONDITION)}
        />
      </FormControl>
    </>
  );
};

export default ConditionsFieldArray;
