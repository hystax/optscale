import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import ConnectCloudAccountForm from "components/forms/ConnectCloudAccountForm";
import PageContentWrapper from "components/PageContentWrapper";
import { CLOUD_ACCOUNTS } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={CLOUD_ACCOUNTS} component={RouterLink}>
      <FormattedMessage id="dataSourcesTitle" />
    </Link>
  ],
  title: {
    text: <FormattedMessage id="connectDataSourceTitle" />
  }
};

const ConnectCloudAccount = ({ isLoading, onSubmit, onCancel }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <ConnectCloudAccountForm isLoading={isLoading} onSubmit={onSubmit} onCancel={onCancel} />
    </PageContentWrapper>
  </>
);

export default ConnectCloudAccount;
