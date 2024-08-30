import InputAdornment from "@mui/material/InputAdornment";
import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isPositiveNumberOrZero, costModelValueMaxFractionDigitsValidation } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.MEMORY_PER_HOUR;

const MemoryPerHourField = () => {
  const { currencySymbol } = useOrganizationInfo();

  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      label={<FormattedMessage id="memoryPerHour" />}
      required
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
      }}
      min={0}
      validate={{
        positiveNumber: (value) => (isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumber" })),
        fractionDigits: costModelValueMaxFractionDigitsValidation
      }}
      dataTestId="input_memory"
    />
  );
};

export default MemoryPerHourField;
