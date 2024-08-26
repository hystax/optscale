import { ReactNode, SyntheticEvent } from "react";
import CloseIcon from "@mui/icons-material/Close";
import WidthNormalIcon from "@mui/icons-material/WidthNormal";
import WidthWideIcon from "@mui/icons-material/WidthWide";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import SideModalTitle from "components/SideModalTitle";
import { capitalize } from "utils/strings";
import useStyles from "./SideModalHeader.styles";

type Title =
  | { text: string; messageId?: never; formattedMessageValues?: never }
  | { text?: never; messageId: string; formattedMessageValues?: Record<string, ReactNode> };

export type SideModalHeaderProps = Title & {
  onClose: (event: SyntheticEvent) => void;
  showExpand?: boolean;
  onExpandChange?: () => void;
  isExpanded?: boolean;
  dataTestIds?: {
    title?: string;
    closeButton?: string;
    expandButton?: string;
  };
  color?: "primary" | "success" | "info" | "error";
};

const SideModalHeader = ({
  text,
  messageId,
  onClose,
  showExpand = false,
  onExpandChange,
  isExpanded,
  formattedMessageValues,
  dataTestIds,
  color = "primary"
}: SideModalHeaderProps) => {
  const { classes, cx } = useStyles();

  const {
    title: titleDataTestId,
    closeButton: closeButtonDataTestId,
    expandButton: expandButtonDataTestId
  } = dataTestIds || {};

  const headerColorClassName = `header${capitalize(color)}` as const;
  const headerClasses = cx(classes[headerColorClassName]);

  return (
    <Box mb={2}>
      <AppBar className={headerClasses} position="static">
        <Toolbar>
          <SideModalTitle dataTestId={titleDataTestId} className={classes.title}>
            {text ?? <FormattedMessage id={messageId} values={formattedMessageValues} />}
          </SideModalTitle>
          {showExpand && (
            <IconButton
              dataTestId={expandButtonDataTestId}
              icon={isExpanded ? <WidthNormalIcon /> : <WidthWideIcon />}
              onClick={onExpandChange}
              color="inherit"
            />
          )}
          <IconButton dataTestId={closeButtonDataTestId} icon={<CloseIcon />} onClick={onClose} color="inherit" />
        </Toolbar>
      </AppBar>
    </Box>
  );
};

export default SideModalHeader;
