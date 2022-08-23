import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { withStyles } from "tss-react/mui";
import FormattedMoney from "components/FormattedMoney";
import IconLabelGrid from "components/IconLabelGrid";
import KeyValueLabel from "components/KeyValueLabel";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import useStyles from "./KeyValueChartTooltipBody.styles";

// TODO: Check the connection between this style and the styles in the style file (https://gitlab.com/hystax/ngui/-/merge_requests/2017#note_637241676)
const TooltipTypography = withStyles(Typography, {
  root: {
    fontSize: "0.9rem"
  }
});

const KeyValueChartTooltipBody = ({ title, boldTitle = false, text, icon, value }) => {
  const { classes } = useStyles();

  const renderLabel = () => (
    <KeyValueLabel
      value={<FormattedMoney value={value} type={FORMATTED_MONEY_TYPES.COMMON} />}
      text={text}
      typographyProps={{
        classes: {
          root: classes.keyValueLabelTypography
        }
      }}
    />
  );

  return (
    <>
      {title ? <TooltipTypography fontWeight={boldTitle ?? "bold"}>{title}</TooltipTypography> : null}
      {icon ? <IconLabelGrid label={renderLabel()} startIcon={icon} /> : renderLabel()}
    </>
  );
};

KeyValueChartTooltipBody.propTypes = {
  value: PropTypes.number,
  title: PropTypes.node,
  boldTitle: PropTypes.bool,
  text: PropTypes.node,
  icon: PropTypes.node
};

export default KeyValueChartTooltipBody;
