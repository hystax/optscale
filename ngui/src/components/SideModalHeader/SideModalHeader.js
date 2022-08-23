import React from "react";
import CloseIcon from "@mui/icons-material/Close";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import SideModalTitle from "components/SideModalTitle";
import { capitalize } from "utils/strings";
import useStyles from "./SideModalHeader.styles";

const SideModalHeader = ({ messageId, onClose, formattedMessageValues, dataTestIds, color = "primary" }) => {
  const { classes, cx } = useStyles();

  const { title: titleDataTestId, closeButton: closeButtonDataTestId } = dataTestIds || {};

  const headerClasses = cx(classes["header".concat(capitalize(color))]);

  return (
    <Box mb={2}>
      <AppBar className={headerClasses} position="static">
        <Toolbar>
          <SideModalTitle dataTestId={titleDataTestId} className={classes.title}>
            <FormattedMessage id={messageId} values={formattedMessageValues} />
          </SideModalTitle>
          <IconButton dataTestId={closeButtonDataTestId} icon={<CloseIcon />} onClick={onClose} color="inherit" />
        </Toolbar>
      </AppBar>
    </Box>
  );
};

SideModalHeader.propTypes = {
  messageId: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
  formattedMessageValues: PropTypes.object,
  dataTestIds: PropTypes.shape({
    title: PropTypes.string,
    closeButton: PropTypes.string
  }),
  color: PropTypes.string
};

export default SideModalHeader;
