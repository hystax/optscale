import React from "react";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";
import useStyles from "./QuestionMark.styles";

const QuestionMark = ({ messageId, messageValues, fontSize = "medium", rightSide = false, dataTestId, className }) => {
  const { classes, cx } = useStyles();

  return (
    <Tooltip title={<FormattedMessage id={messageId} values={messageValues} />} placement="right">
      <HelpOutlineIcon
        data-test-id={dataTestId}
        fontSize={fontSize}
        className={cx(classes.questionMark, rightSide && classes.rightSide, className)}
      />
    </Tooltip>
  );
};

QuestionMark.propTypes = {
  messageId: PropTypes.string.isRequired,
  messageValues: PropTypes.object,
  fontSize: PropTypes.string,
  rightSide: PropTypes.bool,
  dataTestId: PropTypes.string,
  className: PropTypes.string
};

export default QuestionMark;
