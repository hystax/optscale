import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import AssignmentRulesTable from "components/AssignmentRulesTable";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import AssignmentRuleService from "services/AssignmentRuleService";
import { getEditPoolUrl, ASSIGNMENT_RULES } from "urls";
import { isEmpty } from "utils/arrays";

const GetAssignmentRulesContainer = ({ poolId, defaultResourceOwner = "" }) => {
  const { useGet } = AssignmentRuleService();
  const { isLoading, assignmentRules } = useGet({ poolId });

  const shouldRenderWarningMessage = !defaultResourceOwner && !isEmpty(assignmentRules?.rules);

  return (
    <>
      {!isLoading && shouldRenderWarningMessage && (
        <FormattedMessage
          id="rulesWillNotBeAppliedWarning"
          values={{
            link: (chunks) => (
              <Link to={getEditPoolUrl(poolId)} component={RouterLink}>
                {chunks}
              </Link>
            )
          }}
        />
      )}
      <AssignmentRulesTable rules={assignmentRules} poolId={poolId} isLoading={isLoading} />
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
    </>
  );
};

GetAssignmentRulesContainer.propTypes = {
  poolId: PropTypes.string.isRequired,
  defaultResourceOwner: PropTypes.string
};

export default GetAssignmentRulesContainer;
