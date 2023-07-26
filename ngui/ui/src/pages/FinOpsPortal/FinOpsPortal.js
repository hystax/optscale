import React from "react";
import ActionBar from "components/ActionBar";
import FullHeightIframe from "components/FullHeightIframe";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import FinOpsChecklistContainer from "containers/FinOpsChecklistContainer";
import { FINOPS, FINOPS_FEATURES, FINOPS_HOWTOS } from "urls";

const actionBarDefinition = {
  title: {
    messageId: "finOpsPortalTitle",
    dataTestId: "lbl_finops_portal"
  }
};

export const FINOPS_TABS = Object.freeze({
  OVERVIEW: "overview",
  HOWTOS: "howtos",
  CHECKLIST: "checklist"
});

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

const FinOpsPortal = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <TabsWrapper
        tabsProps={{
          keepTabContentMounted: true,
          name: "finops",
          tabs,
          defaultTab: FINOPS_TABS.OVERVIEW
        }}
      />
    </PageContentWrapper>
  </>
);

export default FinOpsPortal;
