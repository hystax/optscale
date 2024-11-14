import { Fragment } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Autocomplete } from "@mui/material";
import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { makeStyles } from "tss-react/mui";
import Button from "components/Button";
import CloudTypeIcon from "components/CloudTypeIcon";
import { Selector, TextInput } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import IconLabel from "components/IconLabel";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import ResourceTypeLabel from "components/ResourceTypeLabel";
import { ItemContent, ItemContentWithDataSourceIcon } from "components/Selector";
import {
  CONDITION_TYPES,
  TAG_IS,
  CLOUD_IS,
  TAG_VALUE_STARTS_WITH,
  TAG_EXISTS,
  DEFAULT_CONDITION,
  ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH,
  RESOURCE_TYPE_IS,
  REGION_IS,
  OPTSCALE_RESOURCE_TYPES
} from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { idx } from "utils/objects";
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

const ConditionsFieldArray = ({ name = FIELD_NAME, isLoading = false, cloudAccounts, resourceTypes, regions }) => {
  const intl = useIntl();

  const { classes, cx } = useStyles();

  const {
    control,
    watch,
    formState: { errors }
  } = useFormContext();

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

  const renderResourceTypeIsAutocompleteField = (field, count) => {
    const NAME = FIELD_NAMES.CONDITIONS_FIELD_ARRAY.RESOURCE_TYPE_IS_FIELD_NAME;

    const fieldName = `${name}.${count}.${NAME}`;
    const fieldError = idx(fieldName.split("."), errors);

    return (
      <Controller
        name={`${name}.${count}.${NAME}`}
        control={control}
        defaultValue={field[NAME] ?? ""}
        rules={{
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          }
        }}
        render={({ field: { value: formFieldValue, onChange, ...rest } }) => (
          <Autocomplete
            freeSolo
            options={resourceTypes.toSorted((resourceTypeA, resourceTypeB) => {
              if (resourceTypeA.type === resourceTypeB.type) {
                return resourceTypeA.name.localeCompare(resourceTypeB.name);
              }

              return resourceTypeA.type.localeCompare(resourceTypeB.type);
            })}
            value={formFieldValue}
            onChange={(event, newValue) => {
              onChange(newValue?.name ?? "");
            }}
            onInputChange={(event, newInputValue) => {
              onChange(newInputValue);
            }}
            isOptionEqualToValue={(option, value) => option.name === value}
            getOptionLabel={(option) => {
              if (typeof option === "string") {
                return option;
              }
              return option.name;
            }}
            renderOption={(props, option) => {
              const getOptionLabel = () => {
                if ([OPTSCALE_RESOURCE_TYPES.CLUSTER, OPTSCALE_RESOURCE_TYPES.ENVIRONMENT].includes(option.type)) {
                  return (
                    <ResourceTypeLabel
                      resourceInfo={{
                        resourceType: option.name,
                        clusterTypeId: option.type === OPTSCALE_RESOURCE_TYPES.CLUSTER,
                        isEnvironment: option.type === OPTSCALE_RESOURCE_TYPES.ENVIRONMENT
                      }}
                    />
                  );
                }

                return option.name;
              };

              return <li {...props}>{getOptionLabel()}</li>;
            }}
            renderInput={(autoCompleteParams) => (
              <Input
                required
                label={<FormattedMessage id="resourceType" />}
                dataTestId={`input_${fieldName}`}
                error={!!fieldError}
                helperText={fieldError?.message}
                {...autoCompleteParams}
                {...rest}
              />
            )}
          />
        )}
      />
    );
  };

  const renderRegionIsAutocompleteField = (field, count) => {
    const NAME = FIELD_NAMES.CONDITIONS_FIELD_ARRAY.REGION_IS_FIELD_NAME;

    const fieldName = `${name}.${count}.${NAME}`;
    const fieldError = idx(fieldName.split("."), errors);

    return (
      <Controller
        name={fieldName}
        control={control}
        defaultValue={field[NAME] ?? ""}
        rules={{
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          }
        }}
        render={({ field: { value: formFieldValue, onChange, ...rest } }) => (
          <Autocomplete
            freeSolo
            options={regions
              // Exclude empty (null) regions
              .filter(Boolean)
              .toSorted((regionA, regionB) => {
                if (regionA.cloud_type === regionB.cloud_type) {
                  return regionA.name.localeCompare(regionB.name);
                }

                return regionA.cloud_type.localeCompare(regionB.cloud_type);
              })}
            value={formFieldValue}
            onChange={(event, newValue) => {
              onChange(newValue?.name ?? "");
            }}
            onInputChange={(event, newInputValue) => {
              onChange(newInputValue);
            }}
            isOptionEqualToValue={(option, value) => option.name === value}
            getOptionLabel={(option) => {
              if (typeof option === "string") {
                return option;
              }
              return option.name;
            }}
            renderOption={(props, option) => (
              <li {...props}>
                <IconLabel icon={<CloudTypeIcon type={option.cloud_type} hasRightMargin />} label={option.name} />
              </li>
            )}
            renderInput={(autoCompleteParams) => (
              <Input
                required
                label={<FormattedMessage id="region" />}
                dataTestId={`input_${fieldName}`}
                error={!!fieldError}
                helperText={fieldError?.message}
                {...autoCompleteParams}
                {...rest}
              />
            )}
          />
        )}
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
        case RESOURCE_TYPE_IS:
          return renderResourceTypeIsAutocompleteField(field, count);
        case REGION_IS:
          return renderRegionIsAutocompleteField(field, count);
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
                disabled={fields.length === 1}
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
