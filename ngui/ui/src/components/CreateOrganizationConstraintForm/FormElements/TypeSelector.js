import React from "react";
import PropTypes from "prop-types";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector from "components/Selector";
import { ANOMALY_TYPES, QUOTAS_AND_BUDGETS_TYPES, TAGGING_POLICY_TYPES } from "utils/constants";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TYPE;

const TypeSelector = ({ types }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  const selectorData = {
    items: types.map((type) => ({
      value: type,
      name: intl.formatMessage({ id: ANOMALY_TYPES[type] || QUOTAS_AND_BUDGETS_TYPES[type] || TAGGING_POLICY_TYPES[type] })
    }))
  };

  return (
    <Controller
      name="type"
      dataTestId={`selector_${FIELD_NAME}`}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: controllerField }) => (
        <Selector
          fullWidth
          required
          error={!!errors[FIELD_NAME]}
          helperText={errors[FIELD_NAME]?.message}
          data={selectorData}
          labelId="type"
          {...controllerField}
        />
      )}
    />
  );
};

TypeSelector.propTypes = {
  types: PropTypes.array.isRequired
};

export default TypeSelector;
