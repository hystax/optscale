import React from "react";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import ConnectCloudAccountForm from "components/ConnectCloudAccountForm";
import PageContentWrapper from "components/PageContentWrapper";

const actionBarDefinition = {
  title: {
    messageId: "connectDataSourceTitle"
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
