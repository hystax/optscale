import React from "react";
import { useParams } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import TtlAnalysisContainer from "containers/TtlAnalysisContainer";

const actionBarDefinition = {
  title: {
    messageId: "ttlAnalysisReport",
    dataTestId: "lbl_ttl_report"
  }
};

const TtlAnalysis = () => {
  const { poolId = "" } = useParams();

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <TtlAnalysisContainer pathPoolId={poolId} />
      </PageContentWrapper>
    </>
  );
};

export default TtlAnalysis;
