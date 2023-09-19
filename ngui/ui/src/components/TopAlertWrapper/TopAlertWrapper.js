import React, { useCallback, useEffect, useMemo } from "react";
import { Box } from "@mui/material";
import { render as renderGithubButton } from "github-buttons";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import { useDispatch } from "react-redux";
import { GET_TOKEN } from "api/auth/actionTypes";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useRootData } from "hooks/useRootData";
import { GITHUB_HYSTAX_OPTSCALE_REPO } from "urls";
import { AZURE_TENANT, ENVIRONMENT } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { updateOrganizationTopAlert as updateOrganizationTopAlertActionCreator } from "./actionCreators";
import { useAllAlertsSelector } from "./selectors";
import TopAlert from "./TopAlert";

export const ALERT_TYPES = Object.freeze({
  DATA_SOURCES_ARE_PROCESSING: 2,
  DATA_SOURCES_PROCEEDED: 3,
  OPEN_SOURCE_ANNOUNCEMENT: 4
});

export const IS_EXISTING_USER = "isExistingUser";

const getEligibleDataSources = (dataSources) => dataSources.filter(({ type }) => ![ENVIRONMENT, AZURE_TENANT].includes(type));

const GitHubInlineButton = ({ children, ariaLabelMessageId, href, dataIcon }) => {
  const intl = useIntl();
  const anchorRef = useCallback((anchor) => {
    if (anchor && anchor.parentNode) {
      renderGithubButton(anchor, (el) => {
        anchor.parentNode.replaceChild(el, anchor);
      });
    }
  }, []);
  return (
    <Box display="inline-block" sx={{ verticalAlign: "middle" }} mx={SPACING_1}>
      <a
        href={href}
        data-icon={dataIcon}
        aria-label={intl.formatMessage({ id: ariaLabelMessageId })}
        data-show-count
        ref={anchorRef}
      >
        {children}
      </a>
    </Box>
  );
};

const TopAlertWrapper = ({ blacklistIds = [] }) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { userId }
  } = useApiData(GET_TOKEN);

  const storedAlerts = useAllAlertsSelector(organizationId);

  const { rootData: isExistingUser = false } = useRootData(IS_EXISTING_USER);

  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

  const { isDataReady: isDataSourceReady } = useApiState(GET_DATA_SOURCES, organizationId);

  const eligibleDataSources = getEligibleDataSources(cloudAccounts);

  const hasDataSourceInProcessing = eligibleDataSources.some(({ last_import_at: lastImportAt }) => lastImportAt === 0);

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
    if (isDataSourceReady && !hasDataSourceInProcessing && isDataSourcedProcessingAlertClosed) {
      updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING, closed: false });
    }
  }, [hasDataSourceInProcessing, isDataSourceReady, storedAlerts, updateOrganizationTopAlert]);

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
        id: ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING,
        condition: isDataSourceReady && hasDataSourceInProcessing,
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
        condition: isDataSourceReady && !hasDataSourceInProcessing && isDataSourcesAreProceedingAlertTriggered,
        getContent: () => <FormattedMessage id="allDataSourcesProcessed" />,
        type: "success",
        triggered: isTriggered(ALERT_TYPES.DATA_SOURCES_PROCEEDED),
        onTrigger: () => {
          updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_PROCEEDED, triggered: true });
        },
        onClose: () => {
          updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_ARE_PROCESSING, closed: false, triggered: false });
          updateOrganizationTopAlert({ id: ALERT_TYPES.DATA_SOURCES_PROCEEDED, closed: false, triggered: false });
        },
        dataTestId: "top_alert_data_proceeded"
      },
      {
        id: ALERT_TYPES.OPEN_SOURCE_ANNOUNCEMENT,
        // isExistingUser — true only if user was logged in/visited optscale before. Set in migrations.
        // organizationId — wont be presented on initial load (so storedAlerts will be empty, so even if banner was closed, we would not know that,
        //                  so we need to wait for organizationId. But if user is not logged in — there also wont be organizationId, so we use next flag)
        // userId — presented after login
        // this check means "condition: not logged in new user (!isExistingUser && !userId) OR new user and we know organization id (!isExistingUser && organizationId)"
        condition: !isExistingUser && (!userId || organizationId),
        getContent: () => (
          <Box sx={{ textAlign: "center" }}>
            <FormattedMessage
              id="openSourceAnnouncement"
              values={{
                star: (chunks) => (
                  <GitHubInlineButton
                    ariaLabelMessageId="starHystaxOnGithub"
                    dataIcon="octicon-star"
                    href={GITHUB_HYSTAX_OPTSCALE_REPO}
                  >
                    {chunks}
                  </GitHubInlineButton>
                )
              }}
            />
          </Box>
        ),
        type: "info",
        triggered: isTriggered(ALERT_TYPES.OPEN_SOURCE_ANNOUNCEMENT),
        onClose: () => {
          updateOrganizationTopAlert({ id: ALERT_TYPES.OPEN_SOURCE_ANNOUNCEMENT, closed: true });
        },
        dataTestId: "top_alert_open_source_announcement"
      }
    ];
  }, [
    storedAlerts,
    isDataSourceReady,
    hasDataSourceInProcessing,
    isExistingUser,
    updateOrganizationTopAlert,
    userId,
    organizationId
  ]);

  const currentAlert = useMemo(
    () =>
      alerts
        .filter(({ condition }) => condition)
        // white list of notifications which might be showed on login page
        .filter(({ id }) => !blacklistIds.includes(id))
        // alerts are processed in order as they present in array => we show first non closed alert
        .find((alertDefinition) => {
          const { closed } = storedAlerts.find(({ id }) => id === alertDefinition.id) || {};
          return !closed;
        }),
    [alerts, blacklistIds, storedAlerts]
  );

  return currentAlert ? <TopAlert alert={currentAlert} /> : null;
};

TopAlertWrapper.propTypes = {
  blacklistIds: PropTypes.array
};

export default TopAlertWrapper;
