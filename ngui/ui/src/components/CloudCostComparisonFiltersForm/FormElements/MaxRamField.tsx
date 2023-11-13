import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { IEC_UNITS } from "components/FormattedDigitalUnit";
import Input from "components/Input";
import { MAX_INT_32 } from "utils/constants";
import { isWholeNumber, notOnlyWhiteSpaces } from "utils/validation";
import { FIELD_NAME as MIN_RAM_FIELD } from "./MinRamField";

export const FIELD_NAME = "maxRam";

const MaxRamField = () => {
  const {
    register,
    formState: { errors, isSubmitted },
    watch,
    trigger
  } = useFormContext();

  const intl = useIntl();

  const minRam = watch(MIN_RAM_FIELD);

  useEffect(() => {
    if (isSubmitted) {
      trigger(FIELD_NAME);
    }
  }, [isSubmitted, minRam, trigger]);

  return (
    <Input
      label={<FormattedMessage id="maxRam" />}
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
          whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true),
          notOnlyWhiteSpaces,
          moreThanMinRam: (value) =>
            Number(value) >= Number(minRam)
              ? true
              : intl.formatMessage(
                  { id: "fieldMoreThanOrEqualToField" },
                  {
                    fieldName1: intl.formatMessage({ id: "maxRam" }),
                    fieldName2: intl.formatMessage({ id: "minRam" })
                  }
                )
        }
      })}
    />
  );
};

export default MaxRamField;
