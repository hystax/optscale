import React from "react";
import PropTypes from "prop-types";
import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import PoolTypeSelector from "components/PoolTypeSelector";
import SelectorLoader from "components/SelectorLoader";
import { POOL_TYPE_BUDGET } from "utils/constants";

const PoolFormTypeSelector = ({ isLoading, inputProps }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <SelectorLoader fullWidth labelId="defaultResourceOwner" isRequired />
  ) : (
    <>
      <Controller
        name="type"
        control={control}
        defaultValue={POOL_TYPE_BUDGET}
        rules={{
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          }
        }}
        render={({ field }) => (
          <PoolTypeSelector
            dataTestId="selector_type"
            {...inputProps}
            {...field}
            error={!!errors.type}
            helperText={errors.type && errors.type.message}
          />
        )}
      />
    </>
  );
};
PoolFormTypeSelector.propTypes = {
  inputProps: PropTypes.object,
  isLoading: PropTypes.bool
};

export default PoolFormTypeSelector;
