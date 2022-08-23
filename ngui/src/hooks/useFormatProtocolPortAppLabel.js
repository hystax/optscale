import { useCallback } from "react";
import { useIntl } from "react-intl";

export const useFormatProtocolPortAppLabel = () => {
  const intl = useIntl();

  return useCallback(
    ({ port, protocol, app }) => {
      if (app) {
        return intl.formatMessage({ id: "securityGroupProtocolPortApp" }, { protocol, port, app });
      }
      return intl.formatMessage({ id: "value/value" }, { value1: port, value2: protocol });
    },
    [intl]
  );
};
