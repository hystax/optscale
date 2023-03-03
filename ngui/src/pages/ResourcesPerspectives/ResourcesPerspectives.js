import React from "react";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import ResourcesPerspectivesComponent from "components/ResourcesPerspectives";

const actionBarDefinition = {
  title: {
    messageId: "perspectives",
    dataTestId: "lbl_perspectives"
  }
};

const ResourcesPerspectives = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <ResourcesPerspectivesComponent />
    </PageContentWrapper>
  </>
);

export default ResourcesPerspectives;
