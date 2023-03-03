import React, { useMemo } from "react";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import OrganizationConstraints from "components/OrganizationConstraints";
import OrganizationConstraintsMocked from "components/OrganizationConstraintsMocked";
import { useShouldRenderConnectCloudAccountMock } from "hooks/useShouldRenderConnectCloudAccountMock";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import { ANOMALY_CREATE } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
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

  const shouldRenderConnectCloudAccountMock = useShouldRenderConnectCloudAccountMock();

  const getBackdropMessageType = () => {
    if (shouldRenderConnectCloudAccountMock) {
      return MESSAGE_TYPES.CLOUD_ACCOUNTS;
    }
    if (isEmptyArray(constraints)) {
      return MESSAGE_TYPES.ANOMALY_DETECTION_POLICY;
    }
    return undefined;
  };

  return (
    <Mocked
      mockCondition={!isLoading && isEmptyArray(constraints)}
      backdropMessageType={getBackdropMessageType()}
      mock={<OrganizationConstraintsMocked actionBarDefinition={actionBarDefinition} />}
    >
      <OrganizationConstraints
        actionBarDefinition={actionBarDefinition}
        constraints={constraints}
        isLoading={isLoading}
        addButtonLink={ANOMALY_CREATE}
      />
    </Mocked>
  );
};

export default AnomaliesContainer;
