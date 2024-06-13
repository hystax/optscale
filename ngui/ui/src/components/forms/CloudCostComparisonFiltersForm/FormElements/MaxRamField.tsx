import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { IEC_UNITS } from "components/FormattedDigitalUnit";
import { NumberInput } from "components/forms/common/fields";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.MAX_RAM;
const MIN_RAM_FIELD = FIELD_NAMES.MIN_RAM;

const MaxRamField = () => {
  const {
    formState: { isSubmitted },
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
    <NumberInput
      name={FIELD_NAME}
      label={<FormattedMessage id="maxRam" />}
      required
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
      min={0}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true),
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
      }}
    />
  );
};

export default MaxRamField;
