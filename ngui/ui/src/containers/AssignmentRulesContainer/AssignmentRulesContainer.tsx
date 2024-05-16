import { useMemo } from "react";
import AssignmentRules, { AssignmentRulesMocked } from "components/AssignmentRules";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import AssignmentRulePriorityService from "services/AssignmentRulePriorityService";
import AssignmentRuleService from "services/AssignmentRuleService";
import PoolsService from "services/PoolsService";
import { isEmpty } from "utils/arrays";

const GET_AVAILABLE_POOLS_PERMISSION = ["MANAGE_POOLS"];

const AssignmentRulesContainer = () => {
  const { useGet } = AssignmentRuleService();
  const { isLoading: isGetAssignmentRulesLoading, assignmentRules } = useGet();

  const { useUpdate } = AssignmentRulePriorityService();
  const { isLoading: isUpdateAssignmentRulePriorityLoading, updatePriority } = useUpdate();

  const { useGetAvailablePools } = PoolsService();
  const getAvailablePoolsParams = useMemo(
    () => ({
      permission: GET_AVAILABLE_POOLS_PERMISSION
    }),
    []
  );
  const { data: managedPools, isLoading: isGetManagedPoolsLoading } = useGetAvailablePools(getAvailablePoolsParams);

  // check if we need to add "isLoading" to the rest of the mock-up pages
  return (
    <Mocked
      mock={<AssignmentRulesMocked />}
      mockCondition={!isGetAssignmentRulesLoading && isEmpty(assignmentRules?.rules)}
      backdropMessageType={MESSAGE_TYPES.ASSIGNMENT_RULES}
    >
      <AssignmentRules
        rules={assignmentRules}
        managedPools={managedPools}
        isLoadingProps={{
          isGetAssignmentRulesLoading,
          isGetManagedPoolsLoading
        }}
        isUpdateLoading={isUpdateAssignmentRulePriorityLoading}
        onUpdatePriority={updatePriority}
      />
    </Mocked>
  );
};

export default AssignmentRulesContainer;
