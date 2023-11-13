import { useState } from "react";
import FileCopyOutlinedIcon from "@mui/icons-material/FileCopyOutlined";
import { IconButton } from "@mui/material";
import TextField from "@mui/material/TextField";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";

const CopyTextField = ({ textToDisplay, textToCopy = textToDisplay, className }) => {
  const [openSuccessTooltip, setOpenSuccessTooltip] = useState(false);

  return (
    <TextField
      size="small"
      value={textToDisplay}
      fullWidth
      className={className}
      InputProps={{
        readOnly: true,
        endAdornment: (
          <CopyToClipboard
            text={textToCopy}
            onCopy={(copiedText, result) => {
              setOpenSuccessTooltip(result);
            }}
          >
            <Tooltip
              leaveDelay={0}
              open={openSuccessTooltip}
              title={<FormattedMessage id="copied" />}
              onMouseOut={() => setOpenSuccessTooltip(false)}
              placement="top"
              disableFocusListener
              disableHoverListener
              disableTouchListener
            >
              <IconButton>
                <FileCopyOutlinedIcon />
              </IconButton>
            </Tooltip>
          </CopyToClipboard>
        )
      }}
    />
  );
};

export default CopyTextField;
