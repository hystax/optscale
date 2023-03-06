import React from "react";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import CreatePoolPolicyFormContainer from "containers/CreatePoolPolicyFormContainer";

const actionBarDefinition = {
  title: {
    messageId: "createPoolPolicyTitle",
    dataTestId: "lbl_create_pool_policy"
  }
};

const CreatePoolPolicy = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <CreatePoolPolicyFormContainer />
    </PageContentWrapper>
  </>
);

export default CreatePoolPolicy;
