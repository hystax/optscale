import React from "react";
import PropTypes from "prop-types";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import PoolTypeIcon from "components/PoolTypeIcon";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

const buildPoolSelectorData = (pools) => ({
  items: pools.map(({ id, name, pool_purpose: poolPurpose }) => ({
    name,
    value: id,
    type: poolPurpose
  }))
});

const AssignmentRuleFormPoolSelector = ({
  name,
  ownerSelectorName,
  readOnly = false,
  pools,
  onPoolChange,
  classes = {},
  isLoading
}) => {
  const {
    control,
    setValue,
    getValues,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  return isLoading ? (
    <SelectorLoader readOnly={readOnly} fullWidth labelId="targetPool" isRequired />
  ) : (
    <Controller
      name={name}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: { onChange, ...rest } }) => (
        <Selector
          readOnly={readOnly}
          dataTestId="selector_target_pool"
          customClass={classes.customClass}
          required
          menuItemIcon={{
            component: PoolTypeIcon,
            getComponentProps: ({ type }) => ({
              type
            })
          }}
          error={!!errors[name]}
          helperText={errors?.[name]?.message}
          data={buildPoolSelectorData(pools)}
          labelId="targetPool"
          onChange={(id) => {
            onPoolChange(id, (owners) => {
              const { default_owner_id: defaultOwnerId } = pools.find((pool) => pool.id === id);

              const currentlySelectedOwner = getValues(ownerSelectorName);

              const newSelectedOwner = owners.find((owner) => owner.id === currentlySelectedOwner)
                ? currentlySelectedOwner
                : defaultOwnerId;

              setValue(ownerSelectorName, newSelectedOwner);
            });

            onChange(id);
          }}
          {...rest}
        />
      )}
    />
  );
};

AssignmentRuleFormPoolSelector.propTypes = {
  name: PropTypes.string.isRequired,
  ownerSelectorName: PropTypes.string.isRequired,
  readOnly: PropTypes.bool,
  pools: PropTypes.array.isRequired,
  onPoolChange: PropTypes.func.isRequired,
  classes: PropTypes.shape({
    customClass: PropTypes.string
  }).isRequired,
  isLoading: PropTypes.bool
};

export default AssignmentRuleFormPoolSelector;
