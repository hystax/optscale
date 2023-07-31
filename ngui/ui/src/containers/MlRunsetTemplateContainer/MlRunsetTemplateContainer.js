import React from "react";
import { useParams } from "react-router-dom";
import MlRunsetTemplate from "components/MlRunsetTemplate";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlRunsetsService from "services/MlRunsetsService";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";
import { getRunsetTemplate, getRunsets } from "utils/mlDemoData/utils";

const DemoContainer = () => {
  const { templateId } = useParams();

  const { runsets, runsCount, totalCost, lastRunsetCost } = getRunsets(templateId);

  return (
    <MlRunsetTemplate
      runsetTemplate={getRunsetTemplate(templateId)}
      runsets={runsets}
      runsCount={runsCount}
      totalCost={totalCost}
      lastRunsetCost={lastRunsetCost}
    />
  );
};

const Container = () => {
  const { templateId } = useParams();

  const { useGetOne: useGetOneRunsetTemplate } = MlRunsetTemplatesService();
  const { isLoading: isGetRunsetTemplateLoading, runsetTemplate } = useGetOneRunsetTemplate(templateId);

  const { useGetAll: useGetAllRunsets } = MlRunsetsService();
  const {
    isLoading: isGetRunsetsLoading,
    data: { runsets, runsCount, totalCost, lastRunsetCost }
  } = useGetAllRunsets(templateId);

  return (
    <MlRunsetTemplate
      isGetRunsetsLoading={isGetRunsetsLoading}
      isGetRunsetTemplateLoading={isGetRunsetTemplateLoading}
      runsetTemplate={runsetTemplate}
      runsets={runsets}
      runsCount={runsCount}
      totalCost={totalCost}
      lastRunsetCost={lastRunsetCost}
    />
  );
};

const MlRunsetTemplateContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlRunsetTemplateContainer;
