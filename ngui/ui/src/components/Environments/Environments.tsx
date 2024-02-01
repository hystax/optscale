import { useEffect, useState, useMemo } from "react";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import { Checkbox, FormControlLabel, Grid, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import BookingsCalendar from "components/BookingsCalendar";
import ButtonGroup from "components/ButtonGroup";
import EnvironmentsTable from "components/EnvironmentsTable";
import Hidden from "components/Hidden";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PageContentWrapper from "components/PageContentWrapper";
import Selector from "components/Selector";
import { ENVIRONMENTS_TOUR_IDS } from "components/Tour";
import { useIsTourAvailableForCurrentBreakpoint } from "components/Tour/hooks";
import { useFilterByPermissions } from "hooks/useAllowedActions";
import { useIsDownMediaQuery } from "hooks/useMediaQueries";
import { ENVIRONMENTS_STATUS_FILTERS, SCOPE_TYPES } from "utils/constants";
import { millisecondsToSeconds } from "utils/datetime";
import { SPACING_1, SPACING_2, SPACING_4 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";

// TODO: maybe move into separate component and use it in ExpensesBreakdownBreakdownByButtonsGroup as well
const ButtonsGroupWithLabel = ({ labelId, buttons, activeButtonIndex, isMobile }) => (
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
      <Grid item style={{ paddingTop: 0 }}>
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
const ENVIRONMENTS_ACCESS_QUERY_PARAMETER = "accessGranted";
const ENVIRONMENTS_STATUS_QUERY_PARAMETER = "filterByStatus";

const Environments = ({
  disableFilters = false,
  environments,
  onUpdateActivity,
  entityId,
  isLoadingProps = {},
  startEnvironmentsTour
}) => {
  const isMobile = useIsDownMediaQuery("sm");
  const isTourAvailableForCurrentBreakpoint = useIsTourAvailableForCurrentBreakpoint();

  const actionBarDefinition = {
    hideItemsOnSmallScreens: false,
    title: {
      messageId: "environments",
      dataTestId: "lbl_environments",
      dataProductTourId: ENVIRONMENTS_TOUR_IDS.HEADER
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
        show: isTourAvailableForCurrentBreakpoint,
        type: "iconButton"
      }
    ]
  };

  const {
    [ENVIRONMENTS_STATUS_QUERY_PARAMETER]: filterByStatusQuery,
    [ENVIRONMENTS_ACCESS_QUERY_PARAMETER]: accessGrantedQuery,
    [ENVIRONMENTS_VIEW_QUERY_PARAMETER]: view
  } = getQueryParams();

  const [showAccessGranted, setShowAccessGranted] = useState(() => accessGrantedQuery ?? true);

  const [activeStatusFilter, setActiveStatusFilter] = useState(
    Object.values(ENVIRONMENTS_STATUS_FILTERS).includes(filterByStatusQuery)
      ? filterByStatusQuery
      : ENVIRONMENTS_STATUS_FILTERS.ALL
  );

  const [activeViewFilter, setActiveViewFilter] = useState(
    Object.values(ENVIRONMENTS_VIEWS).includes(view) ? view : ENVIRONMENTS_VIEWS.TABLE
  );

  useEffect(() => {
    updateQueryParams({
      [ENVIRONMENTS_STATUS_QUERY_PARAMETER]: activeStatusFilter,
      [ENVIRONMENTS_ACCESS_QUERY_PARAMETER]: showAccessGranted,
      [ENVIRONMENTS_VIEW_QUERY_PARAMETER]: activeViewFilter
    });
  }, [activeStatusFilter, activeViewFilter, showAccessGranted]);

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
    if (disableFilters) {
      return environments;
    }

    const nowSecondsTimestamp = millisecondsToSeconds(Date.now());

    const filtered = environments
      .filter(
        (environment) =>
          ({
            [ENVIRONMENTS_STATUS_FILTERS.UNAVAILABLE]: !environment.active,
            [ENVIRONMENTS_STATUS_FILTERS.AVAILABLE]: environment.active && !getActiveBooking(environment, nowSecondsTimestamp),
            [ENVIRONMENTS_STATUS_FILTERS.IN_USE]: environment.active && !!getActiveBooking(environment, nowSecondsTimestamp)
          })[activeStatusFilter] ?? true
      )
      .filter((environment) => (showAccessGranted ? environmentsWithBookingPermissionIds.includes(environment.id) : true));

    return filtered;
  }, [activeStatusFilter, environments, environmentsWithBookingPermissionIds, showAccessGranted, disableFilters]);

  const viewButtonsGroup = Object.values(ENVIRONMENTS_VIEWS).map((filter) => ({
    id: filter,
    messageId: filter,
    action: () => setActiveViewFilter(filter),
    dataTestId: `filter_${filter}_access`
  }));

  const activeViewIndex = viewButtonsGroup.findIndex((button) => button.id === activeViewFilter);

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_1}>
          <Grid item container spacing={isMobile ? SPACING_1 : SPACING_4}>
            <ButtonsGroupWithLabel
              labelId="view"
              buttons={viewButtonsGroup}
              activeButtonIndex={activeViewIndex}
              isMobile={isMobile}
            />
            <Grid
              item
              container
              direction="row"
              spacing={isMobile ? 0 : SPACING_1}
              sx={{ width: "auto", alignItems: "center" }}
            >
              <FormControlLabel
                sx={{ mr: 0 }}
                onChange={() => {
                  setShowAccessGranted((prev) => !prev);
                }}
                control={<Checkbox data-test-id="checkbox_filter_access" checked={showAccessGranted} />}
                label={<FormattedMessage id="onlyAccessibleByMe" />}
              />
            </Grid>
            <Grid
              item
              container
              direction="row"
              spacing={isMobile ? 0 : SPACING_1}
              alignItems="center"
              style={{ width: "auto" }}
            >
              <Selector
                sx={{ "& .MuiInput-input": { display: "flex", alignItems: "center" } }}
                data={{
                  selected: activeStatusFilter,
                  items: Object.values(ENVIRONMENTS_STATUS_FILTERS).map((filter) => ({
                    name: <FormattedMessage id={filter} />,
                    value: filter,
                    dataTestId: `dropdown_item_filter_${filter}`
                  }))
                }}
                renderValue={(value) => (
                  <Typography variant="body2" component="span">
                    <FormattedMessage id={value} />
                  </Typography>
                )}
                size="small"
                variant="standard"
                dataTestId="dropdown_filter_status"
                onChange={(value) => {
                  setActiveStatusFilter(value);
                }}
              />
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <Stack spacing={SPACING_2}>
              <div>
                {activeViewFilter === ENVIRONMENTS_VIEWS.TABLE && (
                  <EnvironmentsTable
                    data={filteredEnvironments}
                    onUpdateActivity={onUpdateActivity}
                    entityId={entityId}
                    isLoadingProps={isLoadingProps}
                  />
                )}
                {activeViewFilter === ENVIRONMENTS_VIEWS.CALENDAR && (
                  <Grid container>
                    <Grid item xs={12} sx={{ minHeight: "600px" }}>
                      <BookingsCalendar environments={filteredEnvironments} isLoadingProps={isLoadingProps} />
                    </Grid>
                  </Grid>
                )}
              </div>
              <div>
                <InlineSeverityAlert messageId="environmentsDescription" messageDataTestId="p_environments_list" />
              </div>
            </Stack>
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

export default Environments;
