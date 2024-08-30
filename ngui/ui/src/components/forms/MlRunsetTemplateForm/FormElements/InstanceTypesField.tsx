import { Fragment } from "react";
import BoltIcon from "@mui/icons-material/Bolt";
import { Autocomplete, Box } from "@mui/material";
import { lighten, darken } from "@mui/system";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Chip from "components/Chip";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import Tooltip from "components/Tooltip";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE, RUNSET_TEMPLATE_INSTANCE_TYPES } from "utils/constants";
import { FIELD_NAMES } from "../constants";

export const FIELD_NAME = FIELD_NAMES.INSTANCE_TYPES; // "instanceTypes";

const InstanceGroupName = ({ groupType }) => <FormattedMessage id={`runsetTemplateInstanceGroupType.${groupType}`} />;

const InstanceTypesField = ({ isLoading }) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        validate: {
          positiveNumber: (value) => (!isEmptyArray(value) ? true : intl.formatMessage({ id: "thisFieldIsRequired" }))
        }
      }}
      render={({ field: { value: formFieldValue, onChange } }) =>
        isLoading ? (
          <InputLoader fullWidth />
        ) : (
          <Autocomplete
            value={formFieldValue}
            multiple
            disableClearable
            clearOnBlur
            onChange={(event, newValue) => {
              onChange(newValue);
            }}
            options={RUNSET_TEMPLATE_INSTANCE_TYPES}
            isOptionEqualToValue={(option, value) => option.name === value.name}
            groupBy={(option) => option.type}
            getOptionLabel={(option) => option.name}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip key={option.name} variant="outlined" color="info" label={option.name} {...getTagProps({ index })} />
              ))
            }
            renderInput={(params) => (
              <Input
                {...params}
                dataTestId="input_instance_types"
                label={<FormattedMessage id="instanceTypes" />}
                required
                error={!!errors[FIELD_NAME]}
                helperText={errors[FIELD_NAME]?.message}
              />
            )}
            renderGroup={(params) => (
              <Fragment key={params.key}>
                <Box
                  sx={(theme) => ({
                    position: "sticky",
                    top: "-8px",
                    padding: "4px 10px",
                    color: theme.palette.primary.main,
                    backgroundColor:
                      theme.palette.mode === "light"
                        ? lighten(theme.palette.primary.light, 0.95)
                        : darken(theme.palette.primary.main, 0.8)
                  })}
                >
                  {params.group === RUNSET_TEMPLATE_INSTANCE_GROUP_TYPE.ACCELERATED_COMPUTING ? (
                    <Box display="flex">
                      <InstanceGroupName groupType={params.group} />
                      <Tooltip title={<FormattedMessage id="gpuBased" />}>
                        <BoltIcon />
                      </Tooltip>
                    </Box>
                  ) : (
                    <InstanceGroupName groupType={params.group} />
                  )}
                </Box>
                <Box sx={{ padding: 0 }}>{params.children}</Box>
              </Fragment>
            )}
          />
        )
      }
    />
  );
};

export default InstanceTypesField;
