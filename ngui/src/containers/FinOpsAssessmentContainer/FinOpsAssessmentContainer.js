import React from "react";
import { useNavigate } from "react-router-dom";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import FinOpsAssessment from "components/FinOpsAssessment";
import DataSourcesService from "services/DataSourcesService";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { FINOPS_PORTAL } from "urls";
import { isEmpty } from "utils/arrays";
import { ENVIRONMENT } from "utils/constants";

const FinOpsAssessmentContainer = () => {
  const { useGetFinOpsAssessment, useUpdateFinOpsAssessment } = OrganizationOptionsService();
  const { isGetFinOpsAssessmentLoading, options, isGetFinOpsAssessmentDataReady } = useGetFinOpsAssessment();
  const { isUpdateFinOpsAssessmentLoading, update, reset } = useUpdateFinOpsAssessment();

  const { useGetDataSources } = DataSourcesService();
  const { isGetDataSourceLoading, dataSources } = useGetDataSources();
  const eligibleDataSources = dataSources.filter(({ type }) => type !== ENVIRONMENT);
  // TODO: logic duplicate from TopAlertWrapper, plus need to do a similar thing inside the name Cell
  const hasDataSourcesInProcessing =
    isEmpty(dataSources) || dataSources.some(({ last_import_at: lastImportAt }) => lastImportAt === 0);

  const { step } = options;

  const navigate = useNavigate();

  const onReset = () => {
    reset().then(() => navigate(FINOPS_PORTAL));
  };

  return (
    <ContentBackdropLoader isLoading={!isGetFinOpsAssessmentDataReady}>
      <FinOpsAssessment
        step={step}
        dataSources={eligibleDataSources}
        hasDataSourcesInProcessing={hasDataSourcesInProcessing}
        onCancelAssignment={onReset}
        onUpdateReport={update}
        isLoadingProps={{ isGetFinOpsAssessmentLoading, isUpdateFinOpsAssessmentLoading, isGetDataSourceLoading }}
      />
    </ContentBackdropLoader>
  );
};

export default FinOpsAssessmentContainer;
