import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import DashedTypography from "components/DashedTypography";
import { isEmpty as isEmptyArray } from "utils/arrays";
import useStyles from "./QuickDatePickerValues.styles";

const QuickValues = ({ titleMessageId, items }) => (
  <>
    <Typography>
      <FormattedMessage id={titleMessageId} />
    </Typography>
    {items.map(({ label, onClick, key, translateValues = {}, dataTestId }) => (
      <DashedTypography dataTestId={dataTestId} key={key} onClick={onClick}>
        <FormattedMessage id={label} values={translateValues} />
      </DashedTypography>
    ))}
  </>
);

const QuickDatePickerValues = ({ titleMessageId, items, orItems = [] }) => {
  const { classes } = useStyles();
  return (
    <Box className={classes.container}>
      <QuickValues titleMessageId={titleMessageId} items={items} />
      {!isEmptyArray(orItems) && <QuickValues titleMessageId="or" items={orItems} />}
    </Box>
  );
};

QuickDatePickerValues.propTypes = {
  titleMessageId: PropTypes.string.isRequired,
  items: PropTypes.array.isRequired,
  orItems: PropTypes.array
};

export default QuickDatePickerValues;
