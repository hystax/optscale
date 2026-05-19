import { Stack, Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import PageContentWrapper from "components/PageContentWrapper";
import { intl as rawIntl } from "translations/react-intl-config";

const DashboardPage = () => {
  const intl = useIntl();

  return (
    <PageContentWrapper>
      <Typography variant="h6" gutterBottom>
        Translations reactiveness
      </Typography>
      <Stack spacing={2}>
        <div>Raw: {rawIntl.formatMessage({ id: "recommendations" })}</div>
        <div>Hook: {intl.formatMessage({ id: "recommendations" })}</div>
        <div>
          Component:&nbsp;
          <FormattedMessage id="recommendations" />
        </div>
      </Stack>
    </PageContentWrapper>
  );
};

export default DashboardPage;
