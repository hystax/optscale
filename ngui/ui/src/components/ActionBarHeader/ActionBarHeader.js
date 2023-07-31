import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ActionBarHeaderLoader from "components/ActionBarHeaderLoader";
import Image from "components/Image";
import PageTitle from "components/PageTitle";
import useStyles from "./ActionBarHeader.styles";

const renderText = (text) => (typeof text === "function" ? text() : text);

const ActionBarHeader = React.forwardRef(({ text, messageId, isLoading, dataTestId, dataProductTourId, logo }, ref) => {
  const { classes } = useStyles();
  const { src = "", alt = "", dataTestId: logoDataTestId, icon = null } = logo || {};

  return isLoading ? (
    <ActionBarHeaderLoader />
  ) : (
    <>
      {src || icon ? (
        <Box className={icon ? "" : classes.logoWrapper} display="flex" mr={0.5} alignItems="center">
          {icon || <Image customClass={classes.logo} src={src} alt={alt} dataTestId={logoDataTestId} />}
        </Box>
      ) : null}
      <PageTitle dataProductTourId={dataProductTourId} dataTestId={dataTestId} className={classes.title} ref={ref}>
        {messageId ? <FormattedMessage id={messageId} /> : renderText(text)}
      </PageTitle>
    </>
  );
});

const textAndMessageIdValidator = (props, propName, componentName) => {
  if (!props.text && !props.messageId) {
    return new Error(`${componentName}: component must have text or messageId`);
  }
  if (props.text && props.messageId) {
    return new Error(`${componentName}: text and messageId properties should not be applied together`);
  }
  if (props.messageId && !(typeof props.messageId === "string" || props.messageId instanceof String)) {
    return new Error(`${componentName}: messageId should be a string`);
  }
  return null;
};

ActionBarHeader.propTypes = {
  text: textAndMessageIdValidator,
  messageId: textAndMessageIdValidator,
  logo: PropTypes.object,
  dataTestId: PropTypes.string,
  dataProductTourId: PropTypes.string,
  isLoading: PropTypes.bool
};

export default ActionBarHeader;
