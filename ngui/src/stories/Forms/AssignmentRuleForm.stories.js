import React from "react";
import { boolean } from "@storybook/addon-knobs";
import AssignmentRuleForm from "components/AssignmentRuleForm";

export default {
  title: "Forms/AssignmentRuleForm"
};

const getReadOnlyProps = () => {
  const poolSelector = boolean("isPoolSelectorReadOnly", false);
  const ownerSelector = boolean("isOwnerSelectorReadOnly", false);
  return {
    poolSelector,
    ownerSelector
  };
};

const getIsLoadingProps = () => {
  const isActiveCheckboxLoading = boolean("isActiveCheckboxLoading", false);
  const isNameInputLoading = boolean("isNameInputLoading", false);
  const isConditionsFieldLoading = boolean("isConditionsFieldLoading", false);
  const isPoolSelectorLoading = boolean("isPoolSelectorLoading", false);
  const isOwnerSelectorLoading = boolean("isOwnerSelectorLoading", false);
  const isSubmitButtonLoading = boolean("isSubmitButtonLoading", false);
  return {
    isActiveCheckboxLoading,
    isNameInputLoading,
    isConditionsFieldLoading,
    isPoolSelectorLoading,
    isOwnerSelectorLoading,
    isSubmitButtonLoading
  };
};

export const basic = () => (
  <AssignmentRuleForm
    onSubmit={() => {}}
    onCancel={() => {}}
    poolOwners={[]}
    pools={[]}
    isEdit={boolean("isEdit", false)}
    isLoadingProps={getIsLoadingProps()}
    readOnlyProps={getReadOnlyProps()}
  />
);
