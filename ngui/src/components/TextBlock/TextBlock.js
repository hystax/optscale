import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import TypographyLoader from "components/TypographyLoader";
import useStyles from "./TextBlock.styles";

const TextBlock = ({ messageId, values = {}, color, additionalCharactersAfterText, isLoading = false, isVisible = true }) => {
  const { classes } = useStyles();
  if (!isVisible) {
    return null;
  }
  return isLoading ? (
    <TypographyLoader key={messageId} linesCount={1} />
  ) : (
    <Typography gutterBottom className={color ? classes[color] : ""}>
      <FormattedMessage id={messageId} values={values} />
      {additionalCharactersAfterText}
    </Typography>
  );
};

TextBlock.propTypes = {
  messageId: PropTypes.string.isRequired,
  values: PropTypes.object,
  isLoading: PropTypes.bool,
  isVisible: PropTypes.bool,
  additionalCharactersAfterText: PropTypes.string,
  color: PropTypes.string
};

export default TextBlock;
