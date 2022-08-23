import React, { useMemo, useState } from "react";
import { MESSAGE_TYPES } from "components/ContentBackdrop";
import K8sRightsizing from "components/K8sRightsizing";
import K8sRightsizingMocked from "components/K8sRightsizing/K8sRightsizingMocked";
import Mocked from "components/Mocked";
import { getBasicRelativeRangesSet } from "components/RelativeDateTimePicker/defaults";
import { useShouldRenderConnectCloudAccountMock } from "hooks/useShouldRenderConnectCloudAccountMock";
import K8sRightsizingService from "services/K8sRightsizingService";
import { KUBERNETES_CNR } from "utils/constants";
import { datetimeToUnix, millisecondsToSeconds } from "utils/datetime";

const actionBarDefinition = {
  title: {
    messageId: "k8sRightsizing",
    dataTestId: "lbl_k8s_rightsizing"
  }
};

const K8sRightsizingContainer = () => {
  const { useGet } = K8sRightsizingService();
  const shouldRenderConnectCloudAccountMock = useShouldRenderConnectCloudAccountMock(KUBERNETES_CNR);
  const basicRelativeRangesSet = useMemo(() => getBasicRelativeRangesSet(), []);
  const firstRange = basicRelativeRangesSet[0];
  const { startDateFn } = firstRange;
  const defaultEndDate = new Date();
  const defaultStartDate = startDateFn(defaultEndDate);
  const [requestParams, setRequestParams] = useState({
    startDate: millisecondsToSeconds(defaultStartDate),
    endDate: datetimeToUnix(defaultEndDate)
  });

  const {
    isLoading,
    k8sRightsizing: { k8s_app_rightsizing: namespaces = [] }
  } = useGet(requestParams);

  const applyFilter = ({ startDate, endDate }) => {
    const params = {
      ...requestParams,
      startDate,
      endDate
    };
    setRequestParams(params);
  };

  return (
    <Mocked
      mock={<K8sRightsizingMocked actionBarDefinition={actionBarDefinition} />}
      mockCondition={shouldRenderConnectCloudAccountMock}
      backdropMessageType={MESSAGE_TYPES.K8S_RIGHTSIZING}
    >
      <K8sRightsizing
        actionBarDefinition={actionBarDefinition}
        namespaces={namespaces}
        applyFilter={applyFilter}
        definedRanges={basicRelativeRangesSet}
        isLoading={isLoading}
      />
    </Mocked>
  );
};

export default K8sRightsizingContainer;
