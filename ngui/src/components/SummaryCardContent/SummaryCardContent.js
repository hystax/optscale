import React, { createRef, useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import QuestionMark from "components/QuestionMark";
import Tooltip from "components/Tooltip";
import { SPACING_1 } from "utils/layouts";
import { isEllipsisActive } from "utils/strings";
import useStyles from "./SummaryCardContent.styles";

const renderString = (value, ref, dataTestId) => (
  <Typography fontWeight="bold" component="div" variant="h5" data-test-id={dataTestId} ref={ref} noWrap>
    {value}
  </Typography>
);

const renderValue = ({ isValueOverflow, value, valueRef, dataTestId }) =>
  isValueOverflow ? (
    <Tooltip placement="top" title={value}>
      {renderString(value, valueRef, dataTestId)}
    </Tooltip>
  ) : (
    renderString(value, valueRef, dataTestId)
  );

const renderWithIcon = ({ value, icon, isValueOverflow, valueRef, valueTestId }) => (
  <Grid container wrap="nowrap" alignItems="baseline" spacing={SPACING_1}>
    <Grid item>{icon}</Grid>
    <Grid item xs={10}>
      {renderValue({ isValueOverflow, value, valueRef, dataTestId: valueTestId })}
    </Grid>
  </Grid>
);

const SummaryCardContent = ({ value, caption, dataTestIds, icon = {}, help = {}, button = {} }) => {
  const { classes } = useStyles();
  const [isValueOverflow, setValueEllipsis] = useState(false);
  const valueRef = createRef();

  const { show: showHelp = false, messageId: helpMessageId, dataTestId: helpDataTestId } = help;
  const { show: showButton = false, icon: buttonIcon } = button;
  const { show: showIcon = false, value: iconValue } = icon;
  const { titleTestId, valueTestId } = dataTestIds || {};

  useEffect(() => {
    setValueEllipsis(isEllipsisActive(valueRef));
  }, [valueRef]);

  return (
    <>
      <Box display="flex" alignItems="center">
        {showIcon
          ? renderWithIcon({ value, icon: iconValue, isValueOverflow, valueRef, valueTestId })
          : renderValue({ isValueOverflow, value, valueRef, dataTestId: valueTestId })}
        {showButton && <span className={classes.icon}>{buttonIcon}</span>}
      </Box>
      <Box display="flex" alignItems="center" maxWidth="100%">
        <Typography data-test-id={titleTestId} variant="caption">
          {caption}
        </Typography>
        {showHelp ? (
          <QuestionMark messageId={helpMessageId} className={classes.questionMark} dataTestId={helpDataTestId} />
        ) : null}
      </Box>
    </>
  );
};

SummaryCardContent.propTypes = {
  value: PropTypes.any,
  rawValue: PropTypes.any,
  caption: PropTypes.any,
  rawCaption: PropTypes.any,
  color: PropTypes.oneOf(["primary", "secondary", "success", "error", "warning"]),
  isLoading: PropTypes.bool,
  help: PropTypes.object,
  button: PropTypes.object,
  icon: PropTypes.object,
  dataTestIds: PropTypes.object
};

export default SummaryCardContent;
