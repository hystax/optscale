import { InputAdornment } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isPositiveNumberOrZero } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.COST;

const CostField = () => {
  const { currencySymbol } = useOrganizationInfo();

  const intl = useIntl();

  return (
    <NumberInput
      name={FIELD_NAME}
      label={<FormattedMessage id="cost" />}
      required
      valueAsNumber
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
      }}
      validate={{
        isPositiveNumberOrZero: (value) =>
          isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumberOrZero" })
      }}
    />
  );
};

export default CostField;
