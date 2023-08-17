import React from "react";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";
import useStyles from "./QuestionMark.styles";

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
}) => {
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

QuestionMark.propTypes = {
  tooltipText: PropTypes.node,
  messageId: PropTypes.string,
  messageValues: PropTypes.object,
  fontSize: PropTypes.string,
  rightSide: PropTypes.bool,
  dataTestId: PropTypes.string,
  className: PropTypes.string,
  Icon: PropTypes.elementType,
  onTooltipTitleClick: PropTypes.func,
  withLeftMargin: PropTypes.bool,
  color: PropTypes.string
};

export default QuestionMark;
