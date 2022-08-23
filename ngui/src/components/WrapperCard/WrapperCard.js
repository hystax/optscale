import React from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import Button from "components/Button";
import IconButton from "components/IconButton";
import Tooltip from "components/Tooltip";
import WidgetTitle from "components/WidgetTitle";
import WrapperCardTitlePdf from "components/WrapperCardTitlePdf/WrapperCardTitlePdf";
import useStyles from "./WrapperCard.styles";

const renderButton = (type, buttonProps) => (type === "icon" ? <IconButton {...buttonProps} /> : <Button {...buttonProps} />);

const renderTitleButton = (options) => {
  const { type, tooltip, buttonProps } = options;
  return tooltip ? <Tooltip title={tooltip.title}>{renderButton(type, buttonProps)}</Tooltip> : renderButton(type, buttonProps);
};

const Title = ({ title, titleButton, dataTestId }) => {
  const titleMessage = <WidgetTitle dataTestId={dataTestId}>{title}</WidgetTitle>;

  const button = titleButton && renderTitleButton(titleButton);

  return button ? (
    <Box display="flex" alignItems="center">
      {titleButton.type === "icon" ? titleMessage : <Box mr={1}>{titleMessage}</Box>}
      {button}
    </Box>
  ) : (
    titleMessage
  );
};

const WrapperCard = React.forwardRef(
  (
    {
      title,
      titleCaption,
      titleButton,
      dataTestIds,
      children,
      className,
      button,
      needAlign = false,
      titlePdf,
      variant = "elevation",
      ...rest
    },
    ref
  ) => {
    const { classes, cx } = useStyles();

    const {
      wrapper: wrapperDataTestId,
      title: titleDataTestId,
      titleCaption: titleCaptionDataTestId,
      button: buttonDataTestId
    } = dataTestIds || {};
    const { show: showButton, href, link, messageId: buttonTextId } = button || {};

    const mainCardClasses = cx(classes.mainCard, classes[className], needAlign ? classes.alignedWrapper : "");

    return (
      <>
        <Card data-test-id={wrapperDataTestId} className={mainCardClasses} variant={variant} {...rest} ref={ref}>
          <CardContent className={classes.card}>
            {title && <Title title={title} titleButton={titleButton} dataTestId={titleDataTestId} />}
            {titleCaption && (
              <Typography variant="caption" data-test-id={titleCaptionDataTestId}>
                {titleCaption}
              </Typography>
            )}
            <div className={classes.content}>{children}</div>
          </CardContent>
          {showButton && (
            <CardActions className={classes.actions}>
              <div className={classes.spacer} />
              <Button dataTestId={buttonDataTestId} variant="text" messageId={buttonTextId} link={link} href={href} />
            </CardActions>
          )}
        </Card>
        {titlePdf && <WrapperCardTitlePdf pdfId={titlePdf.id} renderData={titlePdf.renderData} />}
      </>
    );
  }
);

WrapperCard.propTypes = {
  title: PropTypes.node,
  titleCaption: PropTypes.node,
  titleButton: PropTypes.shape({
    type: PropTypes.oneOf(["icon", "button"]).isRequired,
    tooltip: PropTypes.object,
    buttonProps: PropTypes.object
  }),
  children: PropTypes.node,
  button: PropTypes.object,
  className: PropTypes.string,
  dataTestIds: PropTypes.shape({
    wrapper: PropTypes.string,
    title: PropTypes.string,
    button: PropTypes.string
  }),
  fullWidth: PropTypes.bool,
  enableOverflowVisible: PropTypes.bool,
  needAlign: PropTypes.bool,
  link: (props, propName, componentName) => {
    if (props.button && props.button.link && props.button.href) {
      return new Error(`${componentName}: link and href properties should not be applied together`);
    }
    return null;
  },
  href: (props, propName, componentName) => {
    if (props.button && props.button.link && props.button.href) {
      return new Error(`${componentName}: link and href properties should not be applied together`);
    }
    return null;
  },
  titlePdf: PropTypes.shape({
    id: PropTypes.string.isRequired,
    renderData: PropTypes.func.isRequired
  }),
  variant: PropTypes.string
};

export default WrapperCard;
