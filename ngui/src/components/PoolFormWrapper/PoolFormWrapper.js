import React from "react";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import PoolForm, { FormPropTypes } from "components/PoolForm";

const PoolFormWrapper = ({
  parentPoolName,
  onSubmit,
  onCancel,
  defaultValues = {},
  owners,
  parentPoolId,
  poolId,
  hasSubPools,
  isLoadingProps = {}
}) => {
  const { isGetParentPoolLoading = false, isGetPoolLoading = false } = isLoadingProps;

  const actionBarDefinition = poolId
    ? {
        title: {
          text: <FormattedMessage id="edit{}" values={{ value: defaultValues.name }} />,
          isLoading: isGetPoolLoading,
          dataTestId: "lbl_edit_pool"
        }
      }
    : {
        title: {
          text: <FormattedMessage id="addPoolToTitle" values={{ poolName: parentPoolName }} />,
          isLoading: isGetParentPoolLoading,
          dataTestId: "lbl_add_pool"
        }
      };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Box sx={{ width: { md: "50%" } }}>
          <PoolForm
            defaultValues={defaultValues}
            onSubmit={onSubmit}
            onCancel={onCancel}
            isLoadingProps={isLoadingProps}
            owners={owners}
            parentPoolId={parentPoolId}
            poolId={poolId}
            hasSubPools={hasSubPools}
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

PoolFormWrapper.propTypes = FormPropTypes;

export default PoolFormWrapper;
