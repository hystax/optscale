import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import MlRunsetConfiguration from "components/MlRunsetConfiguration";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlRunsetsService from "services/MlRunsetsService";
import MlRunsetTemplatesService from "services/MlRunsetTemplatesService";
import { getMlRunsetTemplateUrl } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { getRunsetTemplate, getRunsets } from "utils/mlDemoData/utils";

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

const DemoContainer = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();

  const runsetTemplate = getRunsetTemplate(templateId);
  const { runsets } = getRunsets(templateId);

  const getLatestRunset = () => {
    const maxRunsetNumber = Math.max(...runsets.map(({ number }) => number));

    return runsets.find(({ number }) => number === maxRunsetNumber);
  };

  const onCancel = () => navigate(getMlRunsetTemplateUrl(templateId));

  return (
    <MlRunsetConfiguration
      runsetTemplate={runsetTemplate}
      latestRunset={getLatestRunset()}
      onSubmit={() => {}}
      onCancel={onCancel}
    />
  );
};

const Container = () => {
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

const MlRunsetConfigurationContainer = () => {
  const { isDemo } = useOrganizationInfo();

  return isDemo ? <DemoContainer /> : <Container />;
};

export default MlRunsetConfigurationContainer;
