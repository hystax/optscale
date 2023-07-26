import React from "react";
import { useParams } from "react-router-dom";
import ModelDetailsSummary from "components/MlModelDetails/ModelDetailsSummary";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlModelsService from "services/MlModelsService";
import { getModelRecommendations } from "utils/mlDemoData/utils";

const DemoContainer = ({ model, isModelDetailsLoading }) => (
  <ModelDetailsSummary
    model={model}
    recommendations={getModelRecommendations()}
    isModelDetailsLoading={isModelDetailsLoading}
    isGetRecommendationsLoading={false}
  />
);

const Container = ({ model, isModelDetailsLoading }) => {
  const { modelId } = useParams();

  const { useGetModelRecommendations } = MlModelsService();

  const { isLoading: isGetRecommendationsLoading, recommendations } = useGetModelRecommendations(modelId);

  return (
    <ModelDetailsSummary
      model={model}
      recommendations={recommendations}
      isModelDetailsLoading={isModelDetailsLoading}
      isGetRecommendationsLoading={isGetRecommendationsLoading}
    />
  );
};

const MlModelRecommendationsContainer = ({ model, isModelDetailsLoading }) => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? (
    <DemoContainer model={model} isModelDetailsLoading={isModelDetailsLoading} />
  ) : (
    <Container model={model} isModelDetailsLoading={isModelDetailsLoading} />
  );
};

export default MlModelRecommendationsContainer;
