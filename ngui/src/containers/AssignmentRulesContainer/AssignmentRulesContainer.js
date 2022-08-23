import React from "react";
import AssignmentRules, { AssignmentRulesMocked } from "components/AssignmentRules";
import { MESSAGE_TYPES } from "components/ContentBackdrop";
import Mocked from "components/Mocked";
import AssignmentRulePriorityService from "services/AssignmentRulePriorityService";
import AssignmentRuleService from "services/AssignmentRuleService";
import { isEmpty } from "utils/arrays";

const AssignmentRulesContainer = () => {
  const { useGet } = AssignmentRuleService();
  const { isLoading: isGetAssignmentRulesLoading, assignmentRules } = useGet();

  const { useUpdate } = AssignmentRulePriorityService();
  const { isLoading: isUpdateAssignmentRulePriorityLoading, updatePriority } = useUpdate();

  // check if we need to add "isLoading" to the rest of the mock-up pages
  return (
    <Mocked
      mock={<AssignmentRulesMocked />}
      mockCondition={!isGetAssignmentRulesLoading && isEmpty(assignmentRules?.rules)}
      backdropMessageType={MESSAGE_TYPES.ASSIGNMENT_RULES}
    >
      <AssignmentRules
        rules={assignmentRules}
        isLoading={isGetAssignmentRulesLoading}
        isUpdateLoading={isUpdateAssignmentRulePriorityLoading}
        onUpdatePriority={updatePriority}
      />
    </Mocked>
  );
};

export default AssignmentRulesContainer;
