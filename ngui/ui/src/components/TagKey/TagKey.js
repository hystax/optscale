import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";

const TagKey = ({ tagKey }) => (tagKey === null ? <FormattedMessage id="(untagged)" /> : tagKey);

TagKey.propTypes = {
  tagKey: PropTypes.string.isRequired
};

export default TagKey;
