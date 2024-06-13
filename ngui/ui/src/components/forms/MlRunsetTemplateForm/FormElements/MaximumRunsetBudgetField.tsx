import { InputAdornment } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

export const FIELD_NAME = FIELD_NAMES.BUDGET; // "budget";

const MaximumRunsetBudgetField = ({ isLoading = false }) => {
  const intl = useIntl();

  const { currencySymbol } = useOrganizationInfo();

  return (
    <NumberInput
      name={FIELD_NAME}
      dataTestId="input_maximum_runset_budget"
      label={<FormattedMessage id="maximumRunsetBudget" />}
      required
      min={0}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true)
      }}
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
      }}
      isLoading={isLoading}
    />
  );
};

export default MaximumRunsetBudgetField;
