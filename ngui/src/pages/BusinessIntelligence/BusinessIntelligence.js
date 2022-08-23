import React from "react";
import { Typography } from "@mui/material";
import { Box } from "@mui/system";
import { FormattedMessage, useIntl } from "react-intl";
import biPlaceholder from "assets/biPlaceholder.svg";
import ActionBar from "components/ActionBar";
import Button from "components/Button";
import PageContentWrapper from "components/PageContentWrapper";
import WrapperCard from "components/WrapperCard";
import { EMAIL_SUPPORT } from "urls";
import { SPACING_1 } from "utils/layouts";
import useStyles from "./BusinessIntelligence.styles";

const actionBarDefinition = {
  title: {
    messageId: "businessIntelligence"
  }
};

const BusinessIntelligence = () => {
  const { classes, cx } = useStyles();
  const intl = useIntl();

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <WrapperCard>
          <Box className={cx(classes.content, classes.centered)}>
            <div>
              <Box mb={SPACING_1}>
                <img style={{ width: "100%" }} src={biPlaceholder} alt={intl.formatMessage({ id: "biBannerAlt" })} />
              </Box>
              <Typography align="center" variant="h5">
                <FormattedMessage id="biDescription" />
              </Typography>
            </div>
            <div>
              <Button
                color="success"
                variant="contained"
                messageId="biCta"
                href={`mailto:${EMAIL_SUPPORT}`}
                customClass={classes.centered}
                sx={{ mb: SPACING_1 }}
              />
              <div className={classes.centered}>
                <Typography align="center" variant="caption" gutterBottom>
                  <FormattedMessage id="biContact" />
                </Typography>
              </div>
            </div>
          </Box>
        </WrapperCard>
      </PageContentWrapper>
    </>
  );
};

export default BusinessIntelligence;
