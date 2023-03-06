import React from "react";
import PropTypes from "prop-types";
import KeyValueLabelsList from "components/KeyValueLabelsList";
import { ALIBABA_CNR } from "utils/constants";

const AlibabaProperties = ({ accountId, config }) => {
  const { access_key_id: accessKeyId } = config;

  const items = [
    {
      itemKey: "alibabaAccountId",
      messageId: "alibabaAccountId",
      value: accountId,
      dataTestIds: {
        key: `p_${ALIBABA_CNR}_id`,
        value: `p_${ALIBABA_CNR}_value`
      }
    },
    {
      itemKey: "alibabaAccessKeyId",
      messageId: "alibabaAccessKeyId",
      value: accessKeyId,
      dataTestIds: { key: "p_access_key_key", value: "p_access_key_value" }
    }
  ];

  return <KeyValueLabelsList items={items} />;
};

AlibabaProperties.propTypes = {
  accountId: PropTypes.string.isRequired,
  config: PropTypes.shape({
    access_key_id: PropTypes.string
  })
};

export default AlibabaProperties;
