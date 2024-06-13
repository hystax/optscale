import { FormattedMessage, useIntl } from "react-intl";
import { IEC_UNITS } from "components/FormattedDigitalUnit";
import { NumberInput } from "components/forms/common/fields";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.MIN_RAM;

const MinRamField = () => {
  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      label={<FormattedMessage id="minRam" />}
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
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
      }}
    />
  );
};

export default MinRamField;
