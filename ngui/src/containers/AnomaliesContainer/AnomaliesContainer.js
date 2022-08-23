import React, { useMemo } from "react";
import OrganizationConstraints from "components/OrganizationConstraints";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { ANOMALY_CREATE } from "urls";
import { ANOMALY_TYPES } from "utils/constants";

const actionBarDefinition = {
  title: {
    messageId: "anomalyDetectionTitle",
    dataTestId: "lbl_constraints_detection"
  }
};

const AnomaliesContainer = () => {
  const { useGetAll } = OrganizationConstraintsService();
  const types = useMemo(() => Object.keys(ANOMALY_TYPES), []);
  const { isLoading, constraints } = useGetAll(types);

  return (
    <OrganizationConstraints
      actionBarDefinition={actionBarDefinition}
      constraints={constraints}
      isLoading={isLoading}
      addButtonLink={ANOMALY_CREATE}
    />
  );
};

export default AnomaliesContainer;
