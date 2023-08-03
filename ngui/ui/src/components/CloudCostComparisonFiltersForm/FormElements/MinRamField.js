import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { IEC_UNITS } from "components/FormattedDigitalUnit";
import Input from "components/Input";
import { MAX_INT_32 } from "utils/constants";
import { isWholeNumber, notOnlyWhiteSpaces } from "utils/validation";

export const FIELD_NAME = "minRam";

const MinRamField = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Input
      label={<FormattedMessage id="minRam" />}
      required
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      InputProps={{
        endAdornment: (
          <FormattedMessage
            id="digitalUnits"
            values={{
              unit: IEC_UNITS.GIBIBYTE
            }}
          />
        )
      }}
      {...register(FIELD_NAME, {
        min: {
          value: 0,
          message: intl.formatMessage({ id: "moreOrEqual" }, { min: 0 })
        },
        max: {
          value: MAX_INT_32,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
        },
        validate: {
          whole: (value) => {
            console.log(value, value % 1 !== 0 || value < 0);
            return isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true;
          },
          notOnlyWhiteSpaces
        }
      })}
    />
  );
};

export default MinRamField;
