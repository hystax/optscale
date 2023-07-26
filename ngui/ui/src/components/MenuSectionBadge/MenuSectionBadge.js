import React from "react";
import { Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Chip from "components/Chip";

const MenuSectionBadge = ({ messageId }) => (
  <Chip
    label={
      <Typography variant="caption">
        <FormattedMessage id={messageId} />
      </Typography>
    }
    color="primary"
  />
);

MenuSectionBadge.propTypes = {
  messageId: PropTypes.string.isRequired
};

export default MenuSectionBadge;
