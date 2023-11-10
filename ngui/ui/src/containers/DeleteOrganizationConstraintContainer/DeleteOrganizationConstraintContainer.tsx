import { useNavigate } from "react-router-dom";
import DeleteEntity from "components/DeleteEntity";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { ANOMALIES, QUOTAS_AND_BUDGETS, TAGGING_POLICIES } from "urls";
import { ANOMALY_TYPES, QUOTAS_AND_BUDGETS_TYPES, TAGGING_POLICY_TYPES } from "utils/constants";

const DeleteAnomalyContainer = ({ onCancel, id, name, type }) => {
  const navigate = useNavigate();

  const { useDelete } = OrganizationConstraintsService();

  const { deleteOrganizationConstraint, isLoading } = useDelete();

  let messageId = "";
  let successLink = "";
  if (ANOMALY_TYPES[type]) {
    successLink = ANOMALIES;
    messageId = "deleteAnomalyDetectionPolicyQuestion";
  }
  if (QUOTAS_AND_BUDGETS_TYPES[type]) {
    successLink = QUOTAS_AND_BUDGETS;
    messageId = "deleteQuotaAndBudgetPolicyQuestion";
  }
  if (TAGGING_POLICY_TYPES[type]) {
    successLink = TAGGING_POLICIES;
    messageId = "deleteTaggingPolicyQuestion";
  }

  const onSuccess = () => navigate(successLink);

  const onDelete = () => deleteOrganizationConstraint({ id, onSuccess });

  return (
    <DeleteEntity
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId,
        values: {
          strong: (chunks) => <strong>{chunks}</strong>,
          name
        }
      }}
    />
  );
};

export default DeleteAnomalyContainer;
