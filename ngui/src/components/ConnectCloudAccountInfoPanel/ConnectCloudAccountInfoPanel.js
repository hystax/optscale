import React from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import alibabaLogo from "assets/marketplaces/alibaba.svg";
import awsLogo from "assets/marketplaces/aws.svg";
import azureLogo from "assets/marketplaces/azure.svg";
import digitalOceanLogo from "assets/marketplaces/digital-ocean.svg";
import IconLink from "components/IconLink";
import MailTo from "components/MailTo";
import SubTitle from "components/SubTitle";
import { EMAIL_INFO, AWS_MARKETPLACE, AZURE_MARKETPLACE, ALIBABA_MARKETPLACE, DIGITAL_OCEAN_MARKETPLACE } from "urls";
import { SPACING_4 } from "utils/layouts";

const MARKETPLACE_ICON_WIDTH = 75;

const HelpText = ({ title, content, dataTestIds = {}, withMarginBottom = true }) => (
  <Box mb={withMarginBottom ? 2 : 0}>
    <SubTitle dataTestId={dataTestIds.title}>{title}</SubTitle>
    <Typography data-test-id={dataTestIds.content}>{content}</Typography>
  </Box>
);

const icons = [
  {
    link: AWS_MARKETPLACE,
    logo: awsLogo,
    dataTestId: "img_aws_marketplace",
    altMessageId: "aws"
  },
  {
    link: AZURE_MARKETPLACE,
    logo: azureLogo,
    dataTestId: "img_azure_marketplace",
    altMessageId: "azure"
  },
  {
    link: ALIBABA_MARKETPLACE,
    logo: alibabaLogo,
    dataTestId: "img_alibaba_marketplace",
    altMessageId: "alibaba"
  },
  {
    link: DIGITAL_OCEAN_MARKETPLACE,
    logo: digitalOceanLogo,
    dataTestId: "img_digital_ocean_marketplace",
    altMessageId: "digitalOcean"
  }
];

const ConnectCloudAccountInfoPanel = () => (
  <>
    <HelpText
      title={<FormattedMessage id="doIRiskAnythingConnectingMyCloudAccount" />}
      content={
        <FormattedMessage
          id="doIRiskAnythingConnectingMyCloudAccountDescription"
          values={{
            p: (chunks) => <p>{chunks}</p>,
            break: <br />
          }}
        />
      }
      dataTestIds={{
        title: "p_title_do_i_risk",
        content: "p_body_do_i_risk"
      }}
      withMarginBottom={false}
    />
    <HelpText
      title={<FormattedMessage id="iWantToSignNDABeforeConnectingCloudAccount" />}
      content={
        <FormattedMessage
          id="iWantToSignNDABeforeConnectingCloudAccountDescription"
          values={{
            email: (chunks) => <MailTo dataTestId="link_contact_us" email={EMAIL_INFO} text={chunks[0]} />
          }}
        />
      }
      dataTestIds={{
        title: "p_title_sign_an_nda",
        content: "p_body_sign_an_nda"
      }}
    />
    <HelpText
      title={<FormattedMessage id="privateDeploymentOptions" />}
      content={<FormattedMessage id="privateDeploymentOptionsDescription" />}
      dataTestIds={{
        title: "p_title_private_deployment",
        content: "p_body_private_deployment"
      }}
    />
    <Grid container alignItems="center" justifyContent="center" spacing={SPACING_4}>
      {icons.map((icon) => (
        <Grid key={icon.altMessageId} item>
          <Box width={MARKETPLACE_ICON_WIDTH}>
            <IconLink icon={icon} />
          </Box>
        </Grid>
      ))}
    </Grid>
  </>
);

export default ConnectCloudAccountInfoPanel;
