import React, { forwardRef } from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import CopyText from "components/CopyText";
import Tooltip from "components/Tooltip";

const CellCaption = ({ text, tooltipText, enableCaptionTextCopy, copyTextDataTestIds = {}, typographyProps = {} }, ref) => {
  const textElement = enableCaptionTextCopy ? (
    <CopyText text={text} copyIconType="animated" variant="inherit" dataTestIds={copyTextDataTestIds}>
      {text}
    </CopyText>
  ) : (
    text
  );

  return (
    <Typography {...typographyProps} ref={ref} variant="caption">
      {tooltipText ? (
        <Tooltip title={tooltipText} placement="right">
          <span>{textElement}</span>
        </Tooltip>
      ) : (
        textElement
      )}
    </Typography>
  );
};

const ForwardedCellCaption = forwardRef(CellCaption);

ForwardedCellCaption.propTypes = {
  text: PropTypes.string.isRequired,
  enableCaptionTextCopy: PropTypes.bool,
  copyTextDataTestIds: PropTypes.object,
  typographyProps: PropTypes.object,
  tooltipText: PropTypes.string
};

export default ForwardedCellCaption;
