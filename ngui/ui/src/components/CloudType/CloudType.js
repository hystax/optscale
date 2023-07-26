import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useDataSources } from "hooks/useDataSources";
import { CLOUD_ACCOUNT_TYPES_LIST } from "utils/constants";

const CloudType = ({ type }) => {
  const { cloudTypeMessageId } = useDataSources(type);

  return cloudTypeMessageId ? <FormattedMessage id={cloudTypeMessageId} /> : type;
};

CloudType.propTypes = {
  type: PropTypes.oneOf(CLOUD_ACCOUNT_TYPES_LIST)
};

export default CloudType;
