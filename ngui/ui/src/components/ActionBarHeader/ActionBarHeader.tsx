import { forwardRef } from "react";
import Box from "@mui/material/Box";
import { FormattedMessage } from "react-intl";
import ActionBarHeaderLoader from "components/ActionBarHeaderLoader";
import Image from "components/Image";
import PageTitle from "components/PageTitle";
import useStyles from "./ActionBarHeader.styles";

const renderText = (text) => (typeof text === "function" ? text() : text);

const ActionBarHeader = forwardRef(({ text, messageId, isLoading, dataTestId, dataProductTourId, logo }, ref) => {
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

export default ActionBarHeader;
