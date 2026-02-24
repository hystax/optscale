import { Box, Typography } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";
import { FormattedMessage } from "react-intl";
import PageTitle from "components/PageTitle";

const SECONDS_TO_LOAD = 20;

const Loading = () => (
  <>
    <Box px={2}>
      <PageTitle dataTestId="p_preparing_ld" align="center">
        <FormattedMessage id="preparingLiveDemoMessage" />
      </PageTitle>
      <Typography align="center" data-test-id="p_process_ld">
        <FormattedMessage
          id="usuallyTheProcessTakesLessThanSeconds"
          values={{
            value: SECONDS_TO_LOAD,
          }}
        />
      </Typography>
    </Box>
    <Box height={60}>
      <CircularProgress data-test-id="svg_loading" />
    </Box>
  </>
);

export default Loading;
