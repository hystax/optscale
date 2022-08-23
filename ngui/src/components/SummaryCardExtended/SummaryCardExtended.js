import React, { createRef, useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import IconButton from "components/IconButton";
import QuestionMark from "components/QuestionMark";
import Skeleton from "components/Skeleton";
import TitleValue from "components/TitleValue";
import Tooltip from "components/Tooltip";
import { SPACING_1 } from "utils/layouts";
import { isEllipsisActive } from "utils/strings";
import useStyles from "./SummaryCardExtended.styles";

const renderString = (value, ref, dataTestId) => (
  <TitleValue dataTestId={dataTestId} noWrap ref={ref}>
    {value}
  </TitleValue>
);

const renderValue = ({ isValueOverflow, value, valueRef, dataTestId }) =>
  isValueOverflow ? (
    <Tooltip placement="top" title={value}>
      {renderString(value, valueRef, dataTestId)}
    </Tooltip>
  ) : (
    renderString(value, valueRef, dataTestId)
  );

const renderWithIcon = ({ value, icon, isValueOverflow, valueRef, dataTestId }) => (
  <Grid container wrap="nowrap" alignItems="baseline" spacing={SPACING_1}>
    <Grid item>{icon}</Grid>
    <Grid item xs={10}>
      {renderValue({ isValueOverflow, value, valueRef, dataTestId })}
    </Grid>
  </Grid>
);

const SummaryCardExtended = ({
  value,
  caption,
  relativeValue,
  relativeValueCaption,
  dataTestIds,
  color = "primary",
  isLoading = false,
  help = {},
  icon = {},
  button = {}
}) => {
  const { classes, cx } = useStyles();
  const [isValueOverflow, setValueEllipsis] = useState(false);
  const valueRef = createRef();

  const { show: showHelp = false, messageId: helpMessageId, dataTestId: helpDataTestId } = help;
  const { show: showButton = false, icon: buttonIcon, tooltip, onClick, link } = button;
  const { show: showIcon = false, value: iconValue } = icon;
  const { cardTestId, titleTestId, valueTestId } = dataTestIds || {};

  const cardColorClasses = cx(classes.root, classes[color] || "");

  useEffect(() => {
    setValueEllipsis(isEllipsisActive(valueRef));
  }, [valueRef]);

  const dividerClass = cx(classes.marginRight, isValueOverflow ? "" : classes.marginLeft);

  const renderCard = (
    <Card data-test-id={cardTestId} className={cardColorClasses}>
      <CardContent className={classes.content}>
        <Typography data-test-id={titleTestId} color="textSecondary" variant="caption">
          {caption}
        </Typography>
        {showHelp ? <QuestionMark messageId={helpMessageId} fontSize="small" dataTestId={helpDataTestId} /> : null}
        <div className={classes.extendedValue}>
          <Box className={classes.valueWrapper}>
            {showIcon
              ? renderWithIcon({ value, icon: iconValue, isValueOverflow, valueRef, dataTestId: valueTestId })
              : renderValue({ isValueOverflow, value, valueRef, dataTestId: valueTestId })}
            {showButton ? <IconButton icon={buttonIcon} tooltip={tooltip} onClick={onClick} link={link} /> : null}
          </Box>
          <Divider orientation="vertical" className={dividerClass} />
          <TitleValue className={classes.relativeValue}>{relativeValue}</TitleValue>
          <Typography className={classes.relativeValueCaption}>{relativeValueCaption}</Typography>
        </div>
      </CardContent>
    </Card>
  );

  return isLoading ? <Skeleton className={classes.skeleton}>{renderCard}</Skeleton> : renderCard;
};

SummaryCardExtended.propTypes = {
  value: PropTypes.any,
  caption: PropTypes.any,
  relativeValue: PropTypes.any,
  relativeValueCaption: PropTypes.any,
  color: PropTypes.oneOf(["primary", "secondary", "success", "error", "warning"]),
  isLoading: PropTypes.bool,
  dataTestIds: PropTypes.object,
  help: PropTypes.object,
  icon: PropTypes.object,
  button: PropTypes.object
};

export default SummaryCardExtended;
