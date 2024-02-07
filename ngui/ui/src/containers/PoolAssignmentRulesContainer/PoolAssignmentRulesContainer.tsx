import { Stack } from "@mui/material";
import Link from "@mui/material/Link";
import { Link as RouterLink } from "react-router-dom";
import PoolAssignmentRulesTable from "components/AssignmentRulesTable/PoolAssignmentRulesTable";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import AssignmentRuleService from "services/AssignmentRuleService";
import { ASSIGNMENT_RULES } from "urls";
import { SPACING_2 } from "utils/layouts";

const PoolAssignmentRulesContainer = ({ poolId }) => {
  const { useGet } = AssignmentRuleService();
  const { isLoading, assignmentRules } = useGet({ poolId });

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <PoolAssignmentRulesTable rules={assignmentRules} isLoading={isLoading} />
      </div>
      <div>
        <InlineSeverityAlert
          messageId="assignmentRulesTabDescription"
          messageValues={{
            assignmentRulesLink: (chunks) => (
              <Link to={ASSIGNMENT_RULES} component={RouterLink}>
                {chunks}
              </Link>
            )
          }}
        />
      </div>
    </Stack>
  );
};

export default PoolAssignmentRulesContainer;
