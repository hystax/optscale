import React from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import ActionBar from "components/ActionBar";
import MailTo from "components/MailTo";
import PageContentWrapper from "components/PageContentWrapper";
import { EMAIL_SUPPORT } from "urls";
import { SPACING_6 } from "utils/layouts";

const renderCloudItem = (item, key, intl) => (
  <Grid item key={key}>
    <Box width={150}>
      <Link href={item.href} target="_blank" rel="noopener">
        <img src={item.src} alt={intl.formatMessage({ id: item.altMessageId })} />
      </Link>
    </Box>
  </Grid>
);

const LandingPage = ({ titleMessageId, featureMessageId, featureActionMessageId, featureUrl, cloudItemsDefinition = [] }) => {
  const intl = useIntl();
  const actionBarDefinition = {
    title: {
      messageId: titleMessageId
    }
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container direction="column" justifyContent="center" alignItems="center" spacing={6}>
          <Grid item xs={12}>
            <Typography align="center">
              <FormattedMessage
                id="featureComingSoon"
                values={{
                  feature: intl.formatMessage({ id: featureMessageId })
                }}
              />
            </Typography>
            <Typography align="center">
              <FormattedMessage
                id="featureLinkMessage"
                values={{
                  link: (chunks) => (
                    <Link href={featureUrl} target="_blank" rel="noopener">
                      {chunks}
                    </Link>
                  ),
                  action: intl.formatMessage({ id: featureActionMessageId }).toLowerCase()
                }}
              />
            </Typography>
          </Grid>
          <Grid container item justifyContent="center" alignItems="center" spacing={SPACING_6} xs={12}>
            {cloudItemsDefinition.map((item, index) => renderCloudItem(item, index, intl))}
          </Grid>
          <Grid item>
            <Typography align="center">
              <FormattedMessage
                id="mailToMessage"
                values={{
                  email: <MailTo email={EMAIL_SUPPORT} text={EMAIL_SUPPORT} />
                }}
              />
            </Typography>
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

LandingPage.propTypes = {
  titleMessageId: PropTypes.string.isRequired,
  featureMessageId: PropTypes.string.isRequired,
  featureActionMessageId: PropTypes.string.isRequired,
  featureUrl: PropTypes.string.isRequired,
  cloudItemsDefinition: PropTypes.array
};

export default LandingPage;
