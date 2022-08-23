import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import ConnectCloudAccountForm from "components/ConnectCloudAccountForm";
import ConnectCloudAccountInfoPanel from "components/ConnectCloudAccountInfoPanel";
import PageContentWrapper from "components/PageContentWrapper";
import WrapperCard from "components/WrapperCard";
import { SPACING_1 } from "utils/layouts";

const actionBarDefinition = {
  goBack: true,
  title: {
    messageId: "connectDataSourceTitle"
  }
};

const ConnectCloudAccount = ({ isLoading, onSubmit, onCancel }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Grid container spacing={SPACING_1}>
        <Grid item xs={12} lg={6}>
          <WrapperCard needAlign>
            <ConnectCloudAccountForm isLoading={isLoading} onSubmit={onSubmit} onCancel={onCancel} />
          </WrapperCard>
        </Grid>
        <Grid item xs={12} lg={6}>
          <WrapperCard dataTestIds={{ wrapper: "panel_info" }} needAlign>
            <ConnectCloudAccountInfoPanel />
          </WrapperCard>
        </Grid>
      </Grid>
    </PageContentWrapper>
  </>
);

ConnectCloudAccount.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired
};

export default ConnectCloudAccount;
