import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { MAX_INT_32 } from "utils/constants";
import { isWholeNumber, notOnlyWhiteSpaces } from "utils/validation";
import { FIELD_NAME as MIN_CPU_FIELD_NAME } from "./MinCpuField";

export const FIELD_NAME = "maxCpu";

const MaxCpuField = () => {
  const {
    register,
    formState: { errors, isSubmitted },
    watch,
    trigger
  } = useFormContext();

  const intl = useIntl();

  const minCpu = watch(MIN_CPU_FIELD_NAME);

  useEffect(() => {
    if (isSubmitted) {
      trigger(FIELD_NAME);
    }
  }, [isSubmitted, minCpu, trigger]);

  return (
    <Input
      label={<FormattedMessage id="maxCpu" />}
      required
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
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
          moreThanMinCpu: (value) =>
            minCpu.trim() === "" || value.trim() === "" || Number(value) >= Number(minCpu)
              ? true
              : intl.formatMessage(
                  { id: "fieldMoreThanOrEqualToField" },
                  {
                    fieldName1: intl.formatMessage({ id: "maxCpu" }),
                    fieldName2: intl.formatMessage({ id: "minCpu" })
                  }
                )
        }
      })}
    />
  );
};

export default MaxCpuField;
