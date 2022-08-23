import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import AssignmentRulesTable from "components/AssignmentRulesTable";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import PageContentWrapper from "components/PageContentWrapper";
import WrapperCard from "components/WrapperCard";
import { SPACING_2 } from "utils/layouts";

const actionBarDefinition = {
  goBack: true,
  title: {
    messageId: "assignmentRulesTitle",
    dataTestId: "lbl_assignment_rules"
  }
};

const renderCardWithContent = (rules, isLoading, onUpdatePriority) => (
  <WrapperCard>
    <Grid container spacing={SPACING_2}>
      <Grid item xs={12}>
        <AssignmentRulesTable rules={rules} isLoading={isLoading} onUpdatePriority={onUpdatePriority} />
      </Grid>
    </Grid>
  </WrapperCard>
);

const AssignmentRules = ({ rules, onUpdatePriority, isLoading = false, isUpdateLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <ContentBackdropLoader isLoading={isUpdateLoading}>
        {renderCardWithContent(rules, isLoading, onUpdatePriority)}
      </ContentBackdropLoader>
    </PageContentWrapper>
  </>
);

AssignmentRules.propTypes = {
  rules: PropTypes.object.isRequired,
  onUpdatePriority: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  isUpdateLoading: PropTypes.bool
};

export default AssignmentRules;
