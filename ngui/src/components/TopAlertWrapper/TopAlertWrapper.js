import React, { useCallback, useEffect, useMemo } from "react";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { HYSTAX_MARKETPLACES_ANCHOR } from "urls";
import { ENVIRONMENT } from "utils/constants";
import { updateOrganizationTopAlert as updateOrganizationTopAlertActionCreator } from "./actionCreators";
import { useAllAlertsSelector } from "./selectors";
import TopAlert from "./TopAlert";

export const ALERT_TYPES = Object.freeze({
  AVAILABLE_FOR_PRIVATE_DEPLOYMENT: 1,
  DATA_SOURCES_ARE_PROCESSING: 2,
  DATA_SOURCES_PROCEEDED: 3
});

const TopAlertWrapper = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const storedAlerts = useAllAlertsSelector(organizationId);

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  const { isDataReady: isDataSourceReady } = useApiState(GET_CLOUD_ACCOUNTS, organizationId);

  const thereAreOnlyEnvironmentDataSources = cloudAccounts.every(({ type }) => type === ENVIRONMENT);

  const hasDataSourceInProcessing = cloudAccounts.some(
    ({ last_import_at: lastImportAt, type }) => lastImportAt === 0 && type !== ENVIRONMENT
  );

  const updateOrganizationTopAlert = useCallback(
    (alert) => {
      dispatch(updateOrganizationTopAlertActionCreator(organizationId, alert));
    },
    [dispatch, organizationId]
  );

  useEffect(() => {
    const isDataSourcedProcessingAlertClosed = storedAlerts.some(
      ({ id, closed }) => id === ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING && closed
    );

    // "recharging" message about processing if closed, when no items are been processed
    if (
      isDataSourceReady &&
      !thereAreOnlyEnvironmentDataSources &&
      !hasDataSourceInProcessing &&
      isDataSourcedProcessingAlertClosed
    ) {
      updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING, closed: false });
    }
  }, [
    hasDataSourceInProcessing,
    isDataSourceReady,
    thereAreOnlyEnvironmentDataSources,
    storedAlerts,
    updateOrganizationTopAlert
  ]);

  const alerts = useMemo(() => {
    const isDataSourcesAreProceedingAlertTriggered = storedAlerts.some(
      ({ id, triggered }) => id === ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING && triggered
    );

    const isTriggered = (alertId) => {
      const { triggered = false } = storedAlerts.find(({ id }) => id === alertId) || {};
      return triggered;
    };

    return [
      {
        id: ALERT_TYPES.AVAILABLE_FOR_PRIVATE_DEPLOYMENT,
        condition: isDataSourceReady && thereAreOnlyEnvironmentDataSources,
        getContent: () => (
          <FormattedMessage
            id="optscaleIsAvailableForPrivateDeployment"
            values={{
              link: (chunks) => (
                <Link href={HYSTAX_MARKETPLACES_ANCHOR} target="_blank" rel="noopener">
                  {chunks}
                </Link>
              )
            }}
          />
        ),
        onClose: () => {
          updateOrganizationTopAlert({ id: ALERT_TYPES.AVAILABLE_FOR_PRIVATE_DEPLOYMENT, closed: true });
        },
        triggered: isTriggered(ALERT_TYPES.AVAILABLE_FOR_PRIVATE_DEPLOYMENT),
        onTrigger: () => {
          updateOrganizationTopAlert({ id: ALERT_TYPES.AVAILABLE_FOR_PRIVATE_DEPLOYMENT, triggered: true });
        },
        dataTestId: "top_alert_private_deployment"
      },
      {
        id: ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING,
        condition: isDataSourceReady && !thereAreOnlyEnvironmentDataSources && hasDataSourceInProcessing,
        getContent: () => <FormattedMessage id="someDataSourcesAreProcessing" />,
        onClose: () => {
          updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING, closed: true });
        },
        triggered: isTriggered(ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING),
        onTrigger: () => {
          updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING, triggered: true });
        },
        dataTestId: "top_alert_data_processing"
      },
      {
        id: ALERT_TYPES.DATA_SOURCES_PROCEEDED,
        condition:
          isDataSourceReady &&
          !thereAreOnlyEnvironmentDataSources &&
          !hasDataSourceInProcessing &&
          isDataSourcesAreProceedingAlertTriggered,
        getContent: () => <FormattedMessage id="allDataSourcesProcessed" />,
        success: true,
        triggered: isTriggered(ALERT_TYPES.DATA_SOURCES_PROCEEDED),
        onTrigger: () => {
          updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_PROCEEDED, triggered: true });
        },
        onClose: () => {
          updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING, closed: false, triggered: false });
          updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_PROCEEDED, closed: false, triggered: false });
        },
        dataTestId: "top_alert_data_proceeded"
      }
    ];
  }, [
    isDataSourceReady,
    thereAreOnlyEnvironmentDataSources,
    hasDataSourceInProcessing,
    storedAlerts,
    updateOrganizationTopAlert
  ]);

  const currentAlert = useMemo(
    () =>
      alerts
        .filter(({ condition }) => condition)
        // alerts are processed in order as they present in array => we show first non closed alert
        .find((alertDefinition) => {
          const { closed } = storedAlerts.find(({ id }) => id === alertDefinition.id) || {};
          return !closed;
        }),
    [alerts, storedAlerts]
  );

  return currentAlert ? <TopAlert alert={currentAlert} /> : null;
};

export default TopAlertWrapper;
