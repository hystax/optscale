import { Typography } from "@mui/material";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import AddToSlackAccountButtonContainer from "containers/AddToSlackAccountButtonContainer";
import { DOCS_HYSTAX_SLACK_INTEGRATION } from "urls";
import BaseSideModal from "./BaseSideModal";

class SlackIntegrationModal extends BaseSideModal {
  headerProps = {
    messageId: "optScaleSlackIntegrationTitle",
    dataTestIds: {
      title: "lbl_connect_slack",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_connect_slack";

  // eslint-disable-next-line
  get content() {
    return (
      <>
        <Box mb={2}>
          <Typography gutterBottom>
            <FormattedMessage id="slackIntegrationDescription1" />
          </Typography>
          <Typography>
            <FormattedMessage id="slackIntegrationDescription2" />
          </Typography>
        </Box>
        <Box mb={2}>
          <AddToSlackAccountButtonContainer />
        </Box>
        <Typography>
          <FormattedMessage
            id="slackIntegrationDescription3"
            values={{
              link: (chunks) => (
                <Link data-test-id="link_read_more" href={DOCS_HYSTAX_SLACK_INTEGRATION} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              )
            }}
          />
        </Typography>
      </>
    );
  }
}

export default SlackIntegrationModal;
