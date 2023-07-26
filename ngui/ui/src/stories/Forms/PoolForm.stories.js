import React from "react";
import PoolForm from "components/PoolForm";
import { KINDS } from "stories";

export default {
  title: `${KINDS.FORMS}/PoolForm`,
  argTypes: {
    isCreateLoading: { name: "Create loading", control: "boolean", defaultValue: false },
    isPoolOwnersLoading: { name: "Poll owner loading", control: "boolean", defaultValue: false },
    isGetPoolLoading: { name: "Get pool loading", control: "boolean", defaultValue: false },
    isEditLoading: { name: "Edit loading", control: "boolean", defaultValue: false },
    hasSubPools: { name: "With sub pools", control: "boolean", defaultValue: false },
    withParentId: { name: "With parent", control: "boolean", defaultValue: false },
    isEdit: { name: "Edit mode", control: "boolean", defaultValue: false }
  }
};

const getIsLoadingProps = (args) => {
  const isCreateLoading = args.isCreateLoading;
  const isPoolOwnersLoading = args.isPoolOwnersLoading;
  const isGetPoolLoading = args.isGetPoolLoading;
  const isEditLoading = args.isEditLoading;
  return {
    isCreateLoading,
    isPoolOwnersLoading,
    isGetPoolLoading,
    isEditLoading
  };
};

const getIsEdit = (args) => args.isEdit;

export const basic = (args) => (
  <PoolForm
    onSubmit={() => console.log("On submit")}
    onCancel={() => console.log("On submit")}
    poolId={getIsEdit() ? "pool_id" : null}
    parentPoolId={args.withParentId ? "parent_pool_id" : null}
    owners={getIsEdit() ? [] : null}
    hasSubPools={args.hasSubPools}
    isLoadingProps={getIsLoadingProps()}
  />
);
