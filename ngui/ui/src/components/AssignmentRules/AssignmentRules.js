import React from "react";
import { Link } from "@mui/material";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import AssignmentRulesTable from "components/AssignmentRulesTable";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PageContentWrapper from "components/PageContentWrapper";
import { POOLS } from "urls";
import { SPACING_2 } from "utils/layouts";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={POOLS} component={RouterLink}>
      <FormattedMessage id="pools" />
    </Link>
  ],
  title: {
    text: <FormattedMessage id="assignmentRulesTitle" />,
    dataTestId: "lbl_assignment_rules"
  }
};

const renderCardWithContent = (rules, isLoading, onUpdatePriority) => (
  <Grid container spacing={SPACING_2}>
    <Grid item xs={12}>
      <AssignmentRulesTable rules={rules} isLoading={isLoading} onUpdatePriority={onUpdatePriority} />
    </Grid>
  </Grid>
);

const AssignmentRules = ({ rules, onUpdatePriority, isLoading = false, isUpdateLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <ContentBackdropLoader isLoading={isUpdateLoading}>
        {renderCardWithContent(rules, isLoading, onUpdatePriority)}
        <InlineSeverityAlert messageId="assignmentRulesPageDescription" messageDataTestId="p_environments_list" />
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
