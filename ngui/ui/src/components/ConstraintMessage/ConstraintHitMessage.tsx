import { useCallback } from "react";
import { useIntl } from "react-intl";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { CONSTRAINT_MESSAGE_FORMAT, isExpensesLimit, isTtlLimit } from "utils/constraints";
import { format, secondsToMilliseconds, EN_FULL_FORMAT } from "utils/datetime";
import ExpenseMessage from "./ExpenseMessage";
import TtlMessage from "./TtlMessage";

export const useFormatConstraintHitMessage = () => {
  const intl = useIntl();
  const { currency = "USD" } = useOrganizationInfo();

  return useCallback(
    ({ limit, type, formats }) => {
      if (isExpensesLimit(type)) {
        return intl.formatNumber(limit, { format: currency });
      }
      if (isTtlLimit(type)) {
        const { ttl: ttlFormat = CONSTRAINT_MESSAGE_FORMAT.DATETIME } = formats;

        if (ttlFormat === CONSTRAINT_MESSAGE_FORMAT.TEXT) {
          return intl.formatMessage(
            {
              id: "hour"
            },
            {
              value: limit
            }
          );
        }
        if (ttlFormat === CONSTRAINT_MESSAGE_FORMAT.DATETIME) {
          return format(secondsToMilliseconds(limit), EN_FULL_FORMAT);
        }
        if (ttlFormat === CONSTRAINT_MESSAGE_FORMAT.EXPIRES_AT_DATETIME) {
          const key = intl.formatMessage({ id: "expiresAt" });
          const value = format(secondsToMilliseconds(limit), EN_FULL_FORMAT);

          return `${key}: ${value}`;
        }
      }
      return "";
    },
    [currency, intl]
  );
};

const ConstraintHitMessage = ({ limit, type, formats = {} }) => {
  if (isExpensesLimit(type)) {
    return <ExpenseMessage type={type} limit={limit} />;
  }
  if (isTtlLimit(type)) {
    return <TtlMessage type={type} limit={limit} formats={formats} />;
  }
  return null;
};

export default ConstraintHitMessage;
