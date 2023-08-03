import React, { useState, useEffect } from "react";
import K8sRightsizing from "components/K8sRightsizing";
import K8sRightsizingMocked from "components/K8sRightsizing/K8sRightsizingMocked";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import RelativeDateTimePicker, { k8sRightsizingRelativeDates } from "components/RelativeDateTimePicker";
import { useShouldRenderConnectCloudAccountMock } from "hooks/useShouldRenderConnectCloudAccountMock";
import K8sRightsizingService from "services/K8sRightsizingService";
import { KUBERNETES_CNR } from "utils/constants";
import { getQueryParams, updateQueryParams } from "utils/network";

const actionBarDefinition = {
  title: {
    messageId: "k8sRightsizingTitle",
    dataTestId: "lbl_k8s_rightsizing"
  }
};

const RELATIVE_PERIOD_QUERY_PARAMETER_NAME = "period";

const K8sRightsizingContainer = () => {
  const { useGet } = K8sRightsizingService();
  const shouldRenderConnectCloudAccountMock = useShouldRenderConnectCloudAccountMock(KUBERNETES_CNR);

  const { [RELATIVE_PERIOD_QUERY_PARAMETER_NAME]: relativePeriodQueryParameter } = getQueryParams();

  const [requestParams, setRequestParams] = useState(() => {
    const defaultRequestParams =
      k8sRightsizingRelativeDates.find((relativeDate) => relativeDate.id === relativePeriodQueryParameter) ??
      k8sRightsizingRelativeDates[0];

    return {
      startDate: defaultRequestParams.startDateFn(),
      endDate: defaultRequestParams.endDateFn(),
      id: defaultRequestParams.id
    };
  });

  useEffect(() => {
    updateQueryParams({
      [RELATIVE_PERIOD_QUERY_PARAMETER_NAME]: requestParams.id
    });
  }, [requestParams.id]);

  const {
    isLoading,
    k8sRightsizing: { k8s_app_rightsizing: namespaces = [] }
  } = useGet({ startDate: requestParams.startDate, endDate: requestParams.endDate });

  const applyFilter = ({ startDateFn, endDateFn, id }) => {
    setRequestParams((prevState) => ({
      ...prevState,
      id,
      startDate: startDateFn(),
      endDate: endDateFn()
    }));
  };

  const tableActionBarDefinition = {
    show: true,
    definition: {
      /*
        Action bar doesn't support mobile view for "custom" items
        See OS-5925
      */
      hideItemsOnSmallScreens: false,
      items: [
        (tableContext) => ({
          key: "date-range-select",
          dataTestId: "btn_add",
          node: (
            <RelativeDateTimePicker
              definedRanges={k8sRightsizingRelativeDates}
              onChange={(range) => {
                applyFilter(range);
                tableContext.setPageIndex(0);
              }}
            />
          ),
          type: "custom"
        })
      ]
    }
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
        isLoading={isLoading}
        tableActionBarDefinition={tableActionBarDefinition}
      />
    </Mocked>
  );
};

export default K8sRightsizingContainer;
