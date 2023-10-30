import React from "react";
import InputAdornment from "@mui/material/InputAdornment";
import PropTypes from "prop-types";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { useMoneyFormatter } from "components/FormattedMoney";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { FORMATTED_MONEY_TYPES, MAX_INT_32 } from "utils/constants";
import { AUTO_EXTENTION_FIELD_NAME } from "./PoolFormAutoExtendCheckbox";

const PoolFormLimitInput = ({ isLoading, unallocatedLimit, isRootPool = false, isReadOnly = false }) => {
  const {
    register,
    formState: { errors }
  } = useFormContext();
  const { currencySymbol } = useOrganizationInfo();

  const intl = useIntl();
  const moneyFormatter = useMoneyFormatter();

  return isLoading ? (
    <InputLoader margin="normal" fullWidth />
  ) : (
    <Input
      type="number"
      required
      error={!!errors.limit}
      helperText={errors.limit && errors.limit.message}
      label={<FormattedMessage id="limit" />}
      InputProps={{
        startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>,
        readOnly: isReadOnly,
        inputProps: {
          min: 0,
          "data-test-id": "input_limit"
        }
      }}
      {...register("limit", {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        min: {
          value: 0,
          message: intl.formatMessage({ id: "moreOrEqual" }, { min: 0 })
        },
        max: {
          value: MAX_INT_32,
          message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
        },
        validate: (value, formValues) =>
          isRootPool ||
          formValues[AUTO_EXTENTION_FIELD_NAME] ||
          value <= unallocatedLimit ||
          intl.formatMessage(
            { id: "maximumPossibleLimitWithoutExtendingParent" },
            { unallocatedLimit: moneyFormatter(FORMATTED_MONEY_TYPES.COMMON, unallocatedLimit) }
          )
      })}
    />
  );
};
PoolFormLimitInput.propTypes = {
  isLoading: PropTypes.bool,
  unallocatedLimit: PropTypes.number,
  isRootPool: PropTypes.bool,
  isReadOnly: PropTypes.bool
};

export default PoolFormLimitInput;
