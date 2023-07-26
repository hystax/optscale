import React from "react";
import { useNavigate } from "react-router-dom";
import PageLoader from "components/PageLoader";
import TechnicalAudit from "components/TechnicalAudit";
import DataSourcesService from "services/DataSourcesService";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { TECHNICAL_AUDIT } from "urls";
import { isEmpty } from "utils/arrays";
import { ENVIRONMENT } from "utils/constants";

const TechnicalAuditContainer = () => {
  const { useGetTechnicalAudit, useUpdateTechnicalAudit } = OrganizationOptionsService();
  const { isGetTechnicalAuditLoading, options, isGetTechnicalAuditDataReady } = useGetTechnicalAudit();
  const { isUpdateTechnicalAuditLoading, update, reset } = useUpdateTechnicalAudit();

  const { useGetDataSources } = DataSourcesService();
  const { isGetDataSourceLoading, dataSources } = useGetDataSources();
  const eligibleDataSources = dataSources.filter(({ type }) => type !== ENVIRONMENT);
  // TODO: logic duplicate from TopAlertWrapper, plus need to do a similar thing inside the name Cell
  const hasDataSourcesInProcessing =
    isEmpty(dataSources) || dataSources.some(({ last_import_at: lastImportAt }) => lastImportAt === 0);

  const { step } = options;

  const navigate = useNavigate();

  const onReset = () => {
    reset().then(() => navigate(TECHNICAL_AUDIT));
  };

  return isGetTechnicalAuditDataReady ? (
    <TechnicalAudit
      step={step}
      dataSources={eligibleDataSources}
      hasDataSourcesInProcessing={hasDataSourcesInProcessing}
      onCancelApplication={onReset}
      onUpdateApplication={update}
      isLoadingProps={{ isGetTechnicalAuditLoading, isUpdateTechnicalAuditLoading, isGetDataSourceLoading }}
    />
  ) : (
    <PageLoader />
  );
};

export default TechnicalAuditContainer;
