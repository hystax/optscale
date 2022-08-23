import React, { useMemo } from "react";
import { GET_ORGANIZATION_FEATURES } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import FullHeightIframe from "components/FullHeightIframe";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import FinOpsAssessmentContainer from "containers/FinOpsAssessmentContainer";
import FinOpsChecklistContainer from "containers/FinOpsChecklistContainer";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useApiState } from "hooks/useApiState";
import { useOrganizationFeatures } from "hooks/useOrganizationFeatures";
import { FINOPS, FINOPS_FEATURES, FINOPS_HOWTOS } from "urls";

const actionBarDefinition = {
  title: {
    messageId: "finOpsPortalTitle"
  }
};

export const FINOPS_TABS = Object.freeze({
  OVERVIEW: "overview",
  HOWTOS: "howtos",
  CHECKLIST: "checklist",
  ASSESSMENT: "assessment"
});

const getTabs = (showAssessment) => {
  const tabs = [
    {
      title: FINOPS_TABS.OVERVIEW,
      dataTestId: `tab_${FINOPS_TABS.OVERVIEW}`,
      node: (
        <FullHeightIframe
          source={FINOPS_FEATURES}
          iframeTitleMessageId="finopsInPracticeIframeTitle"
          fallbackUrl={FINOPS}
          fallbackMessageId="unableToLoad"
          fallbackButtonMessageId="proceedToFinopsWebsite"
        />
      )
    },
    {
      title: FINOPS_TABS.HOWTOS,
      dataTestId: `tab_${FINOPS_TABS.HOWTOS}`,
      node: (
        <FullHeightIframe
          source={FINOPS_HOWTOS}
          iframeTitleMessageId="howtosIframeTitle"
          fallbackUrl={FINOPS}
          fallbackMessageId="unableToLoad"
          fallbackButtonMessageId="proceedToFinopsWebsite"
        />
      )
    },
    {
      title: FINOPS_TABS.CHECKLIST,
      dataTestId: `tab_${FINOPS_TABS.CHECKLIST}`,
      node: <FinOpsChecklistContainer />
    }
  ];
  if (showAssessment) {
    tabs.push({
      title: FINOPS_TABS.ASSESSMENT,
      dataTestId: `tab_${FINOPS_TABS.ASSESSMENT}`,
      node: <FinOpsAssessmentContainer />
    });
  }
  return tabs;
};

const FinOpsPortal = () => {
  const canRunFinOpsAssessment = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const features = useOrganizationFeatures();

  const { isDataReady: isOrganizationFeaturesReady } = useApiState(GET_ORGANIZATION_FEATURES);

  const { disable_finops_assessment: disableFinOpsAssessment = 0 } = features;

  const showFinOpsAssessmentTab = canRunFinOpsAssessment && disableFinOpsAssessment === 0 && isOrganizationFeaturesReady;

  const tabs = useMemo(() => getTabs(showFinOpsAssessmentTab), [showFinOpsAssessmentTab]);

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <TabsWrapper
          tabsProps={{
            name: "finops",
            tabs,
            defaultTab: FINOPS_TABS.OVERVIEW
          }}
        />
      </PageContentWrapper>
    </>
  );
};

export default FinOpsPortal;
