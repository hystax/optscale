import React, { useEffect, useState, useMemo } from "react";
import EventOutlinedIcon from "@mui/icons-material/EventOutlined";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import TableChartOutlinedIcon from "@mui/icons-material/TableChartOutlined";
import { Box, Grid } from "@mui/material";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import BookingsCalendar from "components/BookingsCalendar";
import ButtonGroup from "components/ButtonGroup";
import EnvironmentsTable from "components/EnvironmentsTable";
import Hidden from "components/Hidden";
import PageContentWrapper from "components/PageContentWrapper";
import ProductTour, { ENVIRONMENTS_TOUR } from "components/ProductTour";
import Selector from "components/Selector";
import WrapperCard from "components/WrapperCard";
import { useFilterByPermissions } from "hooks/useAllowedActions";
import { useIsDownMediaQuery } from "hooks/useMediaQueries";
import {
  ENVIRONMENT_TOUR_IDS_BY_DYNAMIC_FIELDS,
  ENVIRONMENT_SOFTWARE_FIELD,
  ENVIRONMENT_JIRA_TICKETS_FIELD,
  ENVIRONMENTS_STATUS_FILTERS,
  ENVIRONMENTS_ACCESS_FILTERS,
  SCOPE_TYPES
} from "utils/constants";
import { millisecondsToSeconds } from "utils/datetime";
import { SPACING_1, SPACING_4 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";

const Description = () => (
  <Box mb={SPACING_1}>
    <Typography data-test-id="p_environments_list">
      <FormattedMessage id="environmentsDescription" />
    </Typography>
  </Box>
);

// TODO: maybe move into separate component and use it in ExpensesBreakdownBreakdownByButtonsGroup as well
const ButtonsGroupWithLabel = ({ labelDataTestId, labelId, buttons, activeButtonIndex, isMobile }) => (
  <Grid item container direction="row" spacing={isMobile ? 0 : SPACING_1} alignItems="center" style={{ width: "auto" }}>
    <Hidden mode="up" breakpoint="sm">
      <Selector
        data={{
          selected: buttons[activeButtonIndex === -1 ? 0 : activeButtonIndex].id,
          items: buttons.map((button) => ({
            name: <FormattedMessage id={button.messageId} />,
            value: button.id
          }))
        }}
        labelId={labelId}
        onChange={(buttonId) => {
          buttons.find((button) => button.id === buttonId).action();
        }}
      />
    </Hidden>
    <Hidden mode="down" breakpoint="sm">
      <Grid item>
        <Typography data-test-id={labelDataTestId}>
          <FormattedMessage id={labelId} />
        </Typography>
      </Grid>
      <Grid item>
        <ButtonGroup buttons={buttons} activeButtonIndex={activeButtonIndex} />
      </Grid>
    </Hidden>
  </Grid>
);

const ENVIRONMENTS_VIEWS = Object.freeze({
  TABLE: "table",
  CALENDAR: "calendar"
});

const ENVIRONMENTS_VIEW_QUERY_PARAMETER = "view";

const initializeView = () => {
  const { [ENVIRONMENTS_VIEW_QUERY_PARAMETER]: view } = getQueryParams();

  return Object.values(ENVIRONMENTS_VIEWS).includes(view) ? view : ENVIRONMENTS_VIEWS.TABLE;
};

const Environments = ({ environments, onUpdateActivity, entityId, isLoadingProps = {}, startEnvironmentsTour }) => {
  const [view, setView] = useState(initializeView);

  useEffect(() => {
    updateQueryParams({
      [ENVIRONMENTS_VIEW_QUERY_PARAMETER]: view
    });
  }, [view]);

  const actionBarDefinition = {
    hideItemsOnSmallScreens: false,
    title: {
      messageId: "environments",
      dataTestId: "lbl_environments",
      dataProductTourId: "environmentsPageHeader"
    },
    items: [
      {
        key: "help",
        icon: <HelpOutlineOutlinedIcon />,
        action: startEnvironmentsTour,
        tooltip: {
          show: true,
          value: <FormattedMessage id="startTour" values={{ value: <FormattedMessage id="environments" /> }} />
        },
        type: "iconButton"
      },
      {
        key: "switch",
        type: "buttonGroup",
        activeButtonId: view,
        buttons: [
          {
            id: ENVIRONMENTS_VIEWS.TABLE,
            action: () => setView(ENVIRONMENTS_VIEWS.TABLE),
            messageIcon: <TableChartOutlinedIcon />
          },
          {
            id: ENVIRONMENTS_VIEWS.CALENDAR,
            action: () => setView(ENVIRONMENTS_VIEWS.CALENDAR),
            messageIcon: <EventOutlinedIcon />
          }
        ]
      }
    ]
  };

  const { filterByStatus, filterByAccess } = getQueryParams();

  const [activeStatusFilter, setActiveStatusFilter] = useState(
    Object.values(ENVIRONMENTS_STATUS_FILTERS).includes(filterByStatus) ? filterByStatus : ENVIRONMENTS_STATUS_FILTERS.ALL
  );

  const [activeAccessFilter, setActiveAccessFilter] = useState(
    Object.values(ENVIRONMENTS_ACCESS_FILTERS).includes(filterByAccess) ? filterByAccess : ENVIRONMENTS_ACCESS_FILTERS.ALL
  );

  useEffect(() => {
    updateQueryParams({ filterByStatus: activeStatusFilter, filterByAccess: activeAccessFilter });
  }, [activeStatusFilter, activeAccessFilter]);

  const getActiveBooking = ({ shareable_bookings: bookings }, nowSecondsTimestamp) =>
    bookings.find(
      (booking) =>
        booking.acquired_since < nowSecondsTimestamp && (nowSecondsTimestamp < booking.released_at || booking.released_at === 0)
    );

  const environmentsWithBookingPermissionIds = useFilterByPermissions({
    entitiesIds: environments.map(({ id }) => id),
    entitiesType: SCOPE_TYPES.RESOURCE,
    permissions: ["BOOK_ENVIRONMENTS"]
  });

  const filteredEnvironments = useMemo(() => {
    const nowSecondsTimestamp = millisecondsToSeconds(Date.now());

    const filtered = environments
      .filter(
        (environment) =>
          ({
            [ENVIRONMENTS_STATUS_FILTERS.UNAVAILABLE]: !environment.active,
            [ENVIRONMENTS_STATUS_FILTERS.AVAILABLE]: environment.active && !getActiveBooking(environment, nowSecondsTimestamp),
            [ENVIRONMENTS_STATUS_FILTERS.IN_USE]: environment.active && !!getActiveBooking(environment, nowSecondsTimestamp)
          }[activeStatusFilter] ?? true)
      )
      .filter(
        (environment) =>
          ({
            [ENVIRONMENTS_ACCESS_FILTERS.GRANTED]: environmentsWithBookingPermissionIds.includes(environment.id),
            [ENVIRONMENTS_ACCESS_FILTERS.RESTRICTED]: !environmentsWithBookingPermissionIds.includes(environment.id)
          }[activeAccessFilter] ?? true)
      );

    return filtered;
  }, [activeStatusFilter, activeAccessFilter, environments, environmentsWithBookingPermissionIds]);

  const statusButtonsGroup = Object.values(ENVIRONMENTS_STATUS_FILTERS).map((filter) => ({
    id: filter,
    messageId: filter,
    action: () => setActiveStatusFilter(filter),
    dataTestId: `filter_${filter}_status`
  }));

  const accessButtonsGroup = Object.values(ENVIRONMENTS_ACCESS_FILTERS).map((filter) => ({
    id: filter,
    messageId: filter,
    action: () => setActiveAccessFilter(filter),
    dataTestId: `filter_${filter}_access`
  }));

  const activeStatusIndex = statusButtonsGroup.findIndex((button) => button.id === activeStatusFilter);
  const activeAccessIndex = accessButtonsGroup.findIndex((button) => button.id === activeAccessFilter);

  const isMobile = useIsDownMediaQuery("sm");

  return (
    <>
      <ProductTour
        label={ENVIRONMENTS_TOUR}
        steps={[
          {
            content: (
              <FormattedMessage
                id="environmentsPageHeaderTourContent"
                values={{ strong: (chunks) => <strong>{chunks}</strong> }}
              />
            ),
            placement: "auto",
            disableBeacon: true,
            target: "[data-product-tour-id='environmentsPageHeader']"
          },
          {
            content: (
              <FormattedMessage
                id="environmentsAddButtonTourContent"
                values={{ strong: (chunks) => <strong>{chunks}</strong> }}
              />
            ),
            placement: "auto",
            disableBeacon: true,
            target: "[data-product-tour-id='environmentsAddButton']"
          },
          {
            content: <FormattedMessage id="environmentsStatusTourContent" />,
            placement: "auto",
            disableBeacon: true,
            target: "[data-product-tour-id='environmentsStatus']"
          },
          {
            content: <FormattedMessage id="environmentsJiraTicketsTourContent" />,
            placement: "auto",
            disableBeacon: true,
            target: `[data-product-tour-id='${ENVIRONMENT_TOUR_IDS_BY_DYNAMIC_FIELDS[ENVIRONMENT_JIRA_TICKETS_FIELD]}']`
          },
          {
            content: (
              <FormattedMessage
                id="environmentsSoftwareTourContent"
                values={{ strong: (chunks) => <strong>{chunks}</strong> }}
              />
            ),
            placement: "auto",
            disableBeacon: true,
            target: `[data-product-tour-id='${ENVIRONMENT_TOUR_IDS_BY_DYNAMIC_FIELDS[ENVIRONMENT_SOFTWARE_FIELD]}']`
          }
        ]}
      />
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_1}>
          <Grid item container spacing={isMobile ? SPACING_1 : SPACING_4}>
            <ButtonsGroupWithLabel
              labelDataTestId="group_title_status"
              labelId="status"
              buttons={statusButtonsGroup}
              activeButtonIndex={activeStatusIndex}
              isMobile={isMobile}
            />
            <ButtonsGroupWithLabel
              labelDataTestId="group_title_access"
              labelId="access"
              buttons={accessButtonsGroup}
              activeButtonIndex={activeAccessIndex}
              isMobile={isMobile}
            />
          </Grid>
          <Grid item xs={12}>
            <WrapperCard>
              <Description />
              {view === ENVIRONMENTS_VIEWS.TABLE && (
                <EnvironmentsTable
                  data={filteredEnvironments}
                  onUpdateActivity={onUpdateActivity}
                  entityId={entityId}
                  isLoadingProps={isLoadingProps}
                />
              )}
              {view === ENVIRONMENTS_VIEWS.CALENDAR && (
                <Grid container spacing={SPACING_1}>
                  <Grid item xs={12} sx={{ minHeight: "600px" }}>
                    <BookingsCalendar environments={filteredEnvironments} isLoadingProps={isLoadingProps} />
                  </Grid>
                </Grid>
              )}
            </WrapperCard>
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

Environments.propTypes = {
  environments: PropTypes.array.isRequired,
  entityId: PropTypes.string,
  onUpdateActivity: PropTypes.func,
  startEnvironmentsTour: PropTypes.func,
  isLoadingProps: PropTypes.shape({
    isGetEnvironmentsLoading: PropTypes.bool,
    isUpdateEnvironmentLoading: PropTypes.bool,
    isGetResourceAllowedActionsLoading: PropTypes.bool
  })
};

export default Environments;
