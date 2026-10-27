import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import AssignmentRulesTable from "components/AssignmentRulesTable";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import PageContentDescription from "components/PageContentDescription/PageContentDescription";
import PageContentWrapper from "components/PageContentWrapper";
import { POOLS } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={POOLS} component={RouterLink}>
      <FormattedMessage id="pools" />
    </Link>,
  ],
  title: {
    text: <FormattedMessage id="assignmentRulesTitle" />,
    dataTestId: "lbl_assignment_rules",
  },
};

const AssignmentRules = ({ rules, managedPools, onUpdatePriority, isLoadingProps = {}, isUpdateLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <ContentBackdropLoader isLoading={isUpdateLoading}>
        <AssignmentRulesTable
          rules={rules}
          managedPools={managedPools}
          isLoadingProps={isLoadingProps}
          onUpdatePriority={onUpdatePriority}
        />
        <PageContentDescription
          position="bottom"
          alertProps={{
            messageId: "assignmentRulesPageDescription",
            messageDataTestId: "p_environments_list",
          }}
        />
      </ContentBackdropLoader>
    </PageContentWrapper>
  </>
);

export default AssignmentRules;
