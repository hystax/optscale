import { useParams } from "react-router-dom";
import MlRunsetTemplate from "components/MlRunsetTemplate";
import MlRunsetsService from "services/MlRunsetsService";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";

const MlRunsetTemplateContainer = () => {
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

export default MlRunsetTemplateContainer;
