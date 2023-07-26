import React from "react";
import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Input from "components/Input";
import InputLoader from "components/InputLoader";

export const FIELD_NAME = "hyperparameters";
export const getHyperparameterFieldName = (environmentVariableName) => `${FIELD_NAME}.${environmentVariableName}`;

const HyperparameterField = ({ hyperparameters, isLoading }) => {
  const {
    formState: { errors },
    register
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <>
      {Object.entries(hyperparameters).map(([hyperparameterName, environmentVariableName]) => {
        const fieldName = getHyperparameterFieldName(environmentVariableName);

        return (
          <Input
            key={hyperparameterName}
            label={`${hyperparameterName} - ${environmentVariableName}`}
            required
            error={!!errors[FIELD_NAME]?.[environmentVariableName]}
            helperText={errors[FIELD_NAME]?.[environmentVariableName]?.message}
            {...register(fieldName, {
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              }
            })}
          />
        );
      })}
    </>
  );
};

export default HyperparameterField;
