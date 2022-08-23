import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";

const IconLink = ({ icon }) => {
  const intl = useIntl();
  return (
    <Link href={icon.link} target="_blank" rel="noopener">
      <img
        data-test-id={icon.dataTestId}
        style={icon.style}
        src={icon.logo}
        alt={intl.formatMessage({ id: icon.altMessageId })}
      />
    </Link>
  );
};

IconLink.propTypes = {
  icon: PropTypes.object.isRequired
};

export default IconLink;
