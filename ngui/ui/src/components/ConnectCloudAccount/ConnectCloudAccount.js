import React from "react";
import { Link } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import ConnectCloudAccountForm from "components/ConnectCloudAccountForm";
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

ConnectCloudAccount.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired
};

export default ConnectCloudAccount;
