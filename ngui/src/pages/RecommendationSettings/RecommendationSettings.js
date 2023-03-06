import React from "react";
import { FormattedMessage } from "react-intl";
import { useParams } from "react-router-dom";
import ActionBar from "components/ActionBar";
import Error from "components/Error";
import PageContentWrapper from "components/PageContentWrapper";
import { getRecommendationInstanceByType } from "components/RelevantRecommendations";
import RecommendationSettingsContainer from "containers/RecommendationSettingsContainer";

const RecommendationSettings = () => {
  const { recommendationType } = useParams();

  const recommendation = getRecommendationInstanceByType(recommendationType);

  if (recommendation === undefined) {
    return <Error messageId="notFound" />;
  }

  const actionBarDefinition = {
    title: {
      text: (
        <FormattedMessage
          id="recommendationSettings"
          values={{
            recommendationName: <FormattedMessage id={recommendation.messageId} />
          }}
        />
      ),
      dataTestId: "lbl_recommendation settings"
    }
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <RecommendationSettingsContainer
          backendRecommendationType={recommendation.moduleName}
          withExclusions={recommendation.withExclusions}
          withThresholds={recommendation.withThresholds}
          withRightsizingStrategy={recommendation.withRightsizingStrategy}
          withInsecurePorts={recommendation.withInsecurePorts}
        />
      </PageContentWrapper>
    </>
  );
};

export default RecommendationSettings;
