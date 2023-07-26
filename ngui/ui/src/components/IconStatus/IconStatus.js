import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import IconLabel from "components/IconLabel";

const IconStatus = ({ icon: Icon, color, labelMessageId, text }) => (
  <IconLabel
    icon={<Icon fontSize="small" color={color} />}
    label={
      <>
        <FormattedMessage id={labelMessageId} />
        {text && <>&nbsp;({text})</>}
      </>
    }
  />
);

IconStatus.propTypes = {
  icon: PropTypes.object.isRequired,
  labelMessageId: PropTypes.string.isRequired,
  color: PropTypes.string.isRequired,
  text: PropTypes.any
};

export default IconStatus;
