import AssignmentRuleForm from "components/forms/AssignmentRuleForm";

export default {
  component: AssignmentRuleForm,
  argTypes: {
    isPoolSelectorReadOnly: { name: "Pool selector read only", control: "boolean", defaultValue: false },
    isOwnerSelectorReadOnly: { name: "Owner selector read only", control: "boolean", defaultValue: false },
    isActiveCheckboxLoading: { name: "Active checkbox loading", control: "boolean", defaultValue: false },
    isNameInputLoading: { name: "Name input loading", control: "boolean", defaultValue: false },
    isConditionsFieldLoading: { name: "Conditions loading", control: "boolean", defaultValue: false },
    isPoolSelectorLoading: { name: "Pool selector loading", control: "boolean", defaultValue: false },
    isOwnerSelectorLoading: { name: "Owner selector loading", control: "boolean", defaultValue: false },
    isSubmitButtonLoading: { name: "Submit loading", control: "boolean", defaultValue: false },
    isEdit: { name: "Edit mode", control: "boolean", defaultValue: false }
  }
};

const getReadOnlyProps = (args) => {
  const poolSelector = args.isPoolSelectorReadOnly;
  const ownerSelector = args.isOwnerSelectorReadOnly;
  return {
    poolSelector,
    ownerSelector
  };
};

const getIsLoadingProps = (args) => {
  const { isActiveCheckboxLoading } = args;
  const { isNameInputLoading } = args;
  const { isConditionsFieldLoading } = args;
  const { isPoolSelectorLoading } = args;
  const { isOwnerSelectorLoading } = args;
  const { isSubmitButtonLoading } = args;
  return {
    isActiveCheckboxLoading,
    isNameInputLoading,
    isConditionsFieldLoading,
    isPoolSelectorLoading,
    isOwnerSelectorLoading,
    isSubmitButtonLoading
  };
};

export const basic = (args) => (
  <AssignmentRuleForm
    onSubmit={() => {}}
    onCancel={() => {}}
    poolOwners={[]}
    pools={[]}
    isEdit={args.isEdit}
    isLoadingProps={getIsLoadingProps()}
    readOnlyProps={getReadOnlyProps()}
  />
);
