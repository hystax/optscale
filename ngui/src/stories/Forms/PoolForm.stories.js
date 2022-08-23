import React from "react";
import { object, boolean } from "@storybook/addon-knobs";
import PoolForm from "components/PoolForm";
import { KINDS } from "stories";

export default {
  title: `${KINDS.FORMS}/PoolForm`
};

const getIsLoadingProps = () => {
  const isCreateLoading = boolean("isCreateLoading", false);
  const isPoolOwnersLoading = boolean("isPoolOwnersLoading", false);
  const isGetPoolLoading = boolean("isGetPoolLoading", false);
  const isEditLoading = boolean("isEditLoading", false);
  return {
    isCreateLoading,
    isPoolOwnersLoading,
    isGetPoolLoading,
    isEditLoading
  };
};

const getIsEdit = () => boolean("isEdit", false);

export const basic = () => (
  <PoolForm
    onSubmit={() => console.log("On submit")}
    onCancel={() => console.log("On submit")}
    poolId={getIsEdit() ? "pool_id" : null}
    parentPoolId={boolean("withParentId", false) ? "parent_pool_id" : null}
    owners={getIsEdit() ? [] : null}
    hasSubPools={boolean("hasSubPools", false)}
    isLoadingProps={getIsLoadingProps()}
  />
);
