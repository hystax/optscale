import React, { useState } from "react";
import FileCopyOutlinedIcon from "@mui/icons-material/FileCopyOutlined";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";
import useStyles from "./CopyText.styles";

const STATIC = "static";
const ANIMATED = "animated";

const CopyText = ({ text, children, variant, copyIconType = STATIC, dataTestIds = {} }) => {
  const { classes, cx } = useStyles();

  const { text: textDataTestId, button: buttonDataTestId } = dataTestIds;

  const [titleMessageId, setTitleMessageId] = useState("copy");

  return (
    <Typography component="span" variant={variant} className={classes.wrapper} data-test-id={textDataTestId}>
      {children}
      <Typography
        component="span"
        onMouseLeave={() => {
          setTitleMessageId("copy");
        }}
        data-test-id={buttonDataTestId}
        className={cx(classes.copyWrapper, copyIconType === ANIMATED ? "animatedCopyIcon" : "")}
      >
        <CopyToClipboard
          text={text}
          onCopy={(copiedText, result) => {
            if (result) {
              setTitleMessageId("copied");
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
            <FileCopyOutlinedIcon className={classes.copyIconFontSize} />
          </Tooltip>
        </CopyToClipboard>
      </Typography>
    </Typography>
  );
};

CopyText.propTypes = {
  text: PropTypes.string.isRequired,
  children: PropTypes.node,
  copyIconType: PropTypes.oneOf([STATIC, ANIMATED]),
  variant: PropTypes.string,
  dataTestIds: PropTypes.shape({
    text: PropTypes.string,
    button: PropTypes.string
  })
};

export default CopyText;
