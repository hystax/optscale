import React, { useCallback } from "react";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import ConstraintHitMessage, { useFormatConstraintHitMessage } from "./ConstraintHitMessage";

export const useFormatConstraintLimitMessage = () => {
  const intl = useIntl();

  const formatConstraintHitMessage = useFormatConstraintHitMessage();

  return useCallback(
    ({ limit, type, formats }) => {
      if (limit === 0) {
        return intl.formatMessage({ id: "notLimited" });
      }

      return formatConstraintHitMessage({ limit, type, formats });
    },
    [formatConstraintHitMessage, intl]
  );
};

const ConstraintLimitMessage = ({ limit, type, formats = {} }) => {
  if (limit === 0) {
    return <TextWithDataTestId messageId="notLimited" dataTestId={`p_${type}_value`} />;
  }
  return <ConstraintHitMessage limit={limit} type={type} formats={formats} />;
};

ConstraintLimitMessage.propTypes = {
  limit: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  type: PropTypes.string,
  formats: PropTypes.object
};

export default ConstraintLimitMessage;
