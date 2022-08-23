import React from "react";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import PoolForm, { FormPropTypes } from "components/PoolForm";
import WrapperCard from "components/WrapperCard";

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
        goBack: true,
        title: {
          text: <FormattedMessage id="edit{}" values={{ value: defaultValues.name }} />,
          isLoading: isGetPoolLoading,
          dataTestId: "lbl_edit_pool"
        }
      }
    : {
        goBack: true,
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
        <WrapperCard className="halfWidth">
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
        </WrapperCard>
      </PageContentWrapper>
    </>
  );
};

PoolFormWrapper.propTypes = FormPropTypes;

export default PoolFormWrapper;
