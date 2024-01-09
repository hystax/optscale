import { MouseEvent, ReactNode, ComponentType } from "react";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import { SvgIconProps } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";
import useStyles from "./QuestionMark.styles";

type TooltipTitleType =
  | {
      tooltipText: ReactNode;
      messageId?: never;
      messageValues?: never;
      onTooltipTitleClick?: never;
    }
  | {
      tooltipText?: never;
      messageId: string;
      messageValues?: { [key: string]: string };
      onTooltipTitleClick?: (event: MouseEvent<HTMLDivElement>) => void;
    };

type QuestionMarkProps = {
  fontSize?: SvgIconProps["fontSize"];
  rightSide?: boolean;
  dataTestId?: string;
  className?: string;
  Icon?: ComponentType<SvgIconProps>;
  color?: SvgIconProps["color"];
  withLeftMargin?: boolean;
} & TooltipTitleType;

/**
 * TODO: Consider renaming this component to HelpTooltipIcon or InfoTooltipIcon
 */
const QuestionMark = ({
  tooltipText,
  messageId,
  messageValues,
  fontSize = "medium",
  rightSide = false,
  dataTestId,
  className,
  Icon = HelpOutlineIcon,
  onTooltipTitleClick,
  color = "secondary",
  /**
   * TODO: Consider replacing it with a "margin" (or just "m") setting that utilizes theme.spacing(1) as the default left margin.
   */
  withLeftMargin = true
}: QuestionMarkProps) => {
  const { classes, cx } = useStyles();

  return (
    <Tooltip
      title={
        tooltipText ?? (
          <div onClick={onTooltipTitleClick}>
            <FormattedMessage id={messageId} values={messageValues} />
          </div>
        )
      }
      placement="right"
    >
      <Icon
        data-test-id={dataTestId}
        fontSize={fontSize}
        color={color}
        className={cx(classes.questionMark, rightSide && classes.rightSide, withLeftMargin && classes.leftMargin, className)}
      />
    </Tooltip>
  );
};

export default QuestionMark;
