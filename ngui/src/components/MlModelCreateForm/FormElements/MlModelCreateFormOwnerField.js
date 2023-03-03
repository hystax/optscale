import React from "react";
import PropTypes from "prop-types";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

const buildSelectorData = (employees) => ({
  items: employees.map(({ id, name }) => ({
    name,
    value: id
  }))
});

const MlModelCreateFormOwnerField = ({ name, employees = [], isLoading = false }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Controller
      name={name}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: { onChange, ...rest } }) =>
        isLoading ? (
          <SelectorLoader readOnly fullWidth labelId="owner" isRequired />
        ) : (
          <Selector
            dataTestId="selector_owner"
            fullWidth
            required
            error={!!errors[name]}
            helperText={errors?.[name]?.message}
            data={buildSelectorData(employees)}
            labelId="owner"
            onChange={(id) => {
              onChange(id);
            }}
            {...rest}
          />
        )
      }
    />
  );
};

MlModelCreateFormOwnerField.propTypes = {
  name: PropTypes.string.isRequired,
  employees: PropTypes.array,
  isLoading: PropTypes.bool
};

export default MlModelCreateFormOwnerField;
