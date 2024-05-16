import { Link, Stack } from "@mui/material";
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

const AssignmentRules = ({ rules, managedPools, onUpdatePriority, isLoadingProps = {}, isUpdateLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <ContentBackdropLoader isLoading={isUpdateLoading}>
        <Stack spacing={SPACING_2}>
          <div>
            <AssignmentRulesTable
              rules={rules}
              managedPools={managedPools}
              isLoadingProps={isLoadingProps}
              onUpdatePriority={onUpdatePriority}
            />
          </div>
          <div>
            <InlineSeverityAlert messageId="assignmentRulesPageDescription" messageDataTestId="p_environments_list" />
          </div>
        </Stack>
      </ContentBackdropLoader>
    </PageContentWrapper>
  </>
);

export default AssignmentRules;
