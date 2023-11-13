import { forwardRef } from "react";
import Typography from "@mui/material/Typography";
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

export default ForwardedCellCaption;
