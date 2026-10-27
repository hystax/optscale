import InputAdornment from "@mui/material/InputAdornment";
import { FormattedMessage, useIntl } from "react-intl";
import { useMoneyFormatter } from "components/FormattedMoney";
import { NumberInput } from "components/forms/common/fields";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.LIMIT;

type PoolFormLimitInputProps = {
  unallocatedLimit: number;
  isLoading?: boolean;
  isRootPool?: boolean;
  isReadOnly?: boolean;
};

const PoolFormLimitInput = ({
  unallocatedLimit,
  isLoading = false,
  isRootPool = false,
  isReadOnly = false,
}: PoolFormLimitInputProps) => {
  const { currencySymbol } = useOrganizationInfo();

  const intl = useIntl();
  const moneyFormatter = useMoneyFormatter();

  return (
    <NumberInput
      name={FIELD_NAME}
      required
      label={<FormattedMessage id="limit" />}
      isLoading={isLoading}
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>,
        readOnly: isReadOnly,
      }}
      dataTestId="input_limit"
      min={0}
      validate={{
        extendingParent: (value, formValues) =>
          isRootPool ||
          formValues[FIELD_NAMES.AUTO_EXTENSION] ||
          value <= unallocatedLimit ||
          intl.formatMessage(
            { id: "maximumPossibleLimitWithoutExtendingParent" },
            { unallocatedLimit: moneyFormatter(FORMATTED_MONEY_TYPES.COMMON, unallocatedLimit) }
          ),
      }}
    />
  );
};

export default PoolFormLimitInput;
