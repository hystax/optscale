import Link from "@mui/material/Link";
import { Link as RouterLink } from "react-router-dom";
import PoolAssignmentRulesTable from "components/AssignmentRulesTable/PoolAssignmentRulesTable";
import PageContentDescription from "components/PageContentDescription";
import AssignmentRuleService from "services/AssignmentRuleService";
import { ASSIGNMENT_RULES } from "urls";

const PoolAssignmentRulesContainer = ({ poolId }) => {
  const { useGet } = AssignmentRuleService();
  const { isLoading, assignmentRules } = useGet({ poolId });

  return (
    <>
      <PoolAssignmentRulesTable rules={assignmentRules} isLoading={isLoading} />
      <PageContentDescription
        position="bottom"
        alertProps={{
          messageId: "assignmentRulesTabDescription",
          messageValues: {
            assignmentRulesLink: (chunks) => (
              <Link to={ASSIGNMENT_RULES} component={RouterLink}>
                {chunks}
              </Link>
            ),
          },
        }}
      />
    </>
  );
};

export default PoolAssignmentRulesContainer;
