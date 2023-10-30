import React from "react";
import PropTypes from "prop-types";
import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

const buildSelectorData = (data) => ({
  items: data.map((obj) => ({
    name: obj.name,
    value: obj.id
  }))
});

const PoolFormOwnerSelector = ({ isLoading, owners, isReadOnly = false }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Controller
      name="defaultOwnerId"
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: { onChange, ...rest } }) => {
        const data = buildSelectorData(owners);
        return isLoading ? (
          <SelectorLoader fullWidth labelId="defaultResourceOwner" isRequired />
        ) : (
          <Selector
            error={!!errors.defaultOwnerId}
            helperText={errors.defaultOwnerId && errors.defaultOwnerId.message}
            data={data}
            dataTestId="selector_owner"
            labelId="defaultResourceOwner"
            fullWidth
            onChange={(id) => {
              onChange(id);
            }}
            readOnly={isReadOnly}
            {...rest}
          />
        );
      }}
    />
  );
};
PoolFormOwnerSelector.propTypes = {
  owners: PropTypes.array.isRequired,
  isLoading: PropTypes.bool,
  isReadOnly: PropTypes.bool
};

export default PoolFormOwnerSelector;
