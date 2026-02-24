import { useState, ReactNode } from "react";
import FileCopyOutlinedIcon from "@mui/icons-material/FileCopyOutlined";
import { type SxProps, type Theme } from "@mui/material";
import Typography, { TypographyOwnProps } from "@mui/material/Typography";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";

type CopyTextProps = {
  text: string;
  children?: ReactNode;
  variant?: TypographyOwnProps["variant"];
  dataTestIds?: {
    text?: string;
    button?: string;
  };
  Icon?: typeof FileCopyOutlinedIcon;
  dynamicCopyIcon?: boolean;
  copyMessageId?: string;
  copiedMessageId?: string;
  sx?: SxProps<Theme>;
};

const CopyText = ({
  text,
  children,
  variant,
  dataTestIds = {},
  Icon = FileCopyOutlinedIcon,
  dynamicCopyIcon = false,
  copyMessageId = "copy",
  copiedMessageId = "copied",
  sx = {},
}: CopyTextProps) => {
  const { text: textDataTestId, button: buttonDataTestId } = dataTestIds;
  const [titleMessageId, setTitleMessageId] = useState(copyMessageId);
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseLeave = () => {
    setTitleMessageId(copyMessageId);
    setIsHovered(false);
  };

  return (
    <Typography
      component="span"
      variant={variant}
      sx={{
        display: "inline-flex",
        alignItems: "center",
        ...sx,
      }}
      data-test-id={textDataTestId}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
    >
      {children && <span>{children}</span>}
      <Typography
        component="span"
        variant={variant}
        data-test-id={buttonDataTestId}
        sx={(theme) => ({
          cursor: "pointer",
          display: "inline-flex",
          pointerEvents: dynamicCopyIcon && !isHovered ? "none" : "auto",
          visibility: dynamicCopyIcon && !isHovered ? "hidden" : "visible",
          paddingLeft: children ? theme.spacing(0.5) : 0,
        })}
      >
        <CopyToClipboard
          text={text}
          onCopy={(_text: string, result: boolean) => {
            if (result) {
              setTitleMessageId(copiedMessageId);
            }
          }}
        >
          <Tooltip
            leaveDelay={0}
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
