import Link from "@mui/material/Link";
import { Link as RouterLink } from "react-router-dom";
import AssignmentRulesTable from "components/AssignmentRulesTable";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import AssignmentRuleService from "services/AssignmentRuleService";
import { ASSIGNMENT_RULES } from "urls";
import { SPACING_1 } from "utils/layouts";

const GetAssignmentRulesContainer = ({ poolId, interactive }) => {
  const { useGet } = AssignmentRuleService();
  const { isLoading, assignmentRules } = useGet({ poolId });

  return (
    <>
      <AssignmentRulesTable interactive={interactive} rules={assignmentRules} poolId={poolId} isLoading={isLoading} />
      <InlineSeverityAlert
        sx={{ mt: SPACING_1 }}
        messageId="assignmentRulesTabDescription"
        messageValues={{
          assignmentRulesLink: (chunks) => (
            <Link to={ASSIGNMENT_RULES} component={RouterLink}>
              {chunks}
            </Link>
          )
        }}
      />
    </>
  );
};

export default GetAssignmentRulesContainer;
