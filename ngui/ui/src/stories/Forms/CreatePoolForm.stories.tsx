import { CreatePoolForm } from "components/PoolForm";

export default {
  component: CreatePoolForm,
  argTypes: {
    isCreateLoading: { name: "Create loading", control: "boolean", defaultValue: false },
    isPoolOwnersLoading: { name: "Poll owner loading", control: "boolean", defaultValue: false },
    isGetPoolLoading: { name: "Get pool loading", control: "boolean", defaultValue: false },
    isEditLoading: { name: "Edit loading", control: "boolean", defaultValue: false },
    hasSubPools: { name: "With sub-pools", control: "boolean", defaultValue: false },
    withParentId: { name: "With parent", control: "boolean", defaultValue: false },
    isEdit: { name: "Edit mode", control: "boolean", defaultValue: false }
  }
};

const getIsLoadingProps = (args) => {
  const { isCreateLoading } = args;
  const { isPoolOwnersLoading } = args;
  const { isGetPoolLoading } = args;
  const { isEditLoading } = args;
  return {
    isCreateLoading,
    isPoolOwnersLoading,
    isGetPoolLoading,
    isEditLoading
  };
};

const getIsEdit = (args) => args.isEdit;

export const basic = (args) => (
  <CreatePoolForm
    onSubmit={() => console.log("On submit")}
    onCancel={() => console.log("On submit")}
    poolId={getIsEdit(args) ? "pool_id" : null}
    parentPoolId={args.withParentId ? "parent_pool_id" : null}
    owners={getIsEdit(args) ? [] : null}
    hasSubPools={args.hasSubPools}
    isLoadingProps={getIsLoadingProps(args)}
  />
);
