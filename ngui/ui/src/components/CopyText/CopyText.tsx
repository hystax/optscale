import { useState } from "react";
import FileCopyOutlinedIcon from "@mui/icons-material/FileCopyOutlined";
import Typography from "@mui/material/Typography";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";
import useStyles from "./CopyText.styles";

const STATIC = "static";
const ANIMATED = "animated";

const CopyText = ({
  text,
  children,
  variant,
  copyIconType = STATIC,
  dataTestIds = {},
  Icon = FileCopyOutlinedIcon,
  copyMessageId = "copy",
  copiedMessageId = "copied",
  sx = {}
}) => {
  const { classes, cx } = useStyles();

  const { text: textDataTestId, button: buttonDataTestId } = dataTestIds;

  const [titleMessageId, setTitleMessageId] = useState(copyMessageId);

  const { display = "flex", alignItems = "center", ...restSx } = sx;

  return (
    <Typography
      component="span"
      variant={variant}
      sx={{
        display,
        alignItems,
        ...restSx
      }}
      className={classes.wrapper}
      data-test-id={textDataTestId}
    >
      {children}
      <Typography
        component="span"
        onMouseLeave={() => {
          setTitleMessageId(copyMessageId);
        }}
        variant={variant}
        data-test-id={buttonDataTestId}
        className={cx(classes.copyWrapper, copyIconType === ANIMATED ? "animatedCopyIcon" : "")}
      >
        <CopyToClipboard
          text={text}
          onCopy={(copiedText, result) => {
            if (result) {
              setTitleMessageId(copiedMessageId);
            }
          }}
        >
          <Tooltip
            leaveDelay={0}
            // force a re-render to hide the tooltip immediately after changing the "titleMessageId"
            key={titleMessageId}
            title={<FormattedMessage id={titleMessageId} />}
            placement="top"
            disableFocusListener
            disableTouchListener
          >
            <Icon fontSize="inherit" />
          </Tooltip>
        </CopyToClipboard>
      </Typography>
    </Typography>
  );
};

export default CopyText;
