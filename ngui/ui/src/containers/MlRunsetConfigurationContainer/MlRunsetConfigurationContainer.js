import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import MlRunsetConfiguration from "components/MlRunsetConfiguration";
import MlRunsetsService from "services/MlRunsetsService";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";
import { getMlRunsetTemplateUrl } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";

const useLatestRunset = () => {
  const { templateId } = useParams();

  const getLatestRunset = (runsets) => {
    const maxRunsetNumber = Math.max(...runsets.map(({ number }) => number));

    return runsets.find(({ number }) => number === maxRunsetNumber);
  };

  const { useGetAll: useGetAllRunsets } = MlRunsetsService();
  const { isLoading, data } = useGetAllRunsets(templateId);
  const { runsets = [] } = data;

  return {
    isLoading,
    latestRunset: isEmptyArray(runsets) ? {} : getLatestRunset(runsets)
  };
};

const MlRunsetConfigurationContainer = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();

  const { useGetOne: useGetRunsetTemplate } = MlRunsetTemplatesService();
  const { isLoading: isGetRunsetTemplateLoading, runsetTemplate } = useGetRunsetTemplate(templateId);

  const { isLoading: isGetLatestRunsetLoading, latestRunset } = useLatestRunset();

  const { useCreate: useCreateRunset } = MlRunsetsService();
  const { onCreate: onCreateRunset, isLoading: isCreateRunsetLoading } = useCreateRunset();

  const redirect = () => navigate(getMlRunsetTemplateUrl(templateId));

  const onSubmit = (formData) => onCreateRunset(templateId, formData).then(() => redirect());

  const onCancel = () => redirect();

  return (
    <MlRunsetConfiguration
      runsetTemplate={runsetTemplate}
      latestRunset={latestRunset}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={{
        isGetRunsetTemplateLoading,
        isGetLatestRunsetLoading,
        isCreateRunsetLoading
      }}
    />
  );
};

export default MlRunsetConfigurationContainer;
