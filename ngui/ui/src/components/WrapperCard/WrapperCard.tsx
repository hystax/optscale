import { forwardRef } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
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

const WrapperCard = forwardRef(
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

    const mainCardClasses = cx(classes[className], needAlign ? classes.alignedWrapper : "");

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

export default WrapperCard;
