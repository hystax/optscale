import React, { useEffect, useState, useMemo } from "react";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import FilterListOutlinedIcon from "@mui/icons-material/FilterListOutlined";
import InfoIcon from "@mui/icons-material/Info";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Accordion from "components/Accordion";
import ActionBar from "components/ActionBar";
import EventsFilter from "components/EventsFilter";
import IconButton from "components/IconButton";
import PageContentWrapper from "components/PageContentWrapper";
import Table from "components/Table";
import { useInitialMount } from "hooks/useInitialMount";
import { isEmpty } from "utils/arrays";
import { formatUTC } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";
import { getQueryParams, updateQueryParams, removeQueryParam } from "utils/network";
import useStyles from "./Events.styles";

const Loader = () => (
  <Box textAlign="center" pt={2}>
    <CircularProgress />
  </Box>
);

export default function Events({ isLoading, onScroll, applyFilter, events }) {
  const [expanded, setExpanded] = useState("");
  const [open, setOpen] = useState(true);
  const { classes, cx } = useStyles();
  const queryParams = getQueryParams();

  const handleAccordion = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : "");
    if (isExpanded) {
      updateQueryParams({ event: panel });
    } else {
      removeQueryParam("event");
    }
  };

  const handleDrawer = () => {
    setOpen(!open);
  };

  const { isInitialMount, setIsInitialMount } = useInitialMount();

  useEffect(() => {
    if (isInitialMount) {
      setIsInitialMount(false);
    } else if (queryParams.event) {
      setExpanded(queryParams.event);
    }
  }, [setExpanded, queryParams, isInitialMount, setIsInitialMount]);

  const addIcon = (level) =>
    ({
      INFO: <InfoIcon className={cx(classes.tableIcon, classes.infoIcon)} />,
      SUCCESS: <CheckCircleIcon className={cx(classes.tableIcon, classes.successIcon)} />,
      WARNING: <ErrorIcon className={cx(classes.tableIcon, classes.warningIcon)} />,
      ERROR: <ErrorIcon color="error" className={classes.tableIcon} />
    }[level]);

  const eventTableColumns = useMemo(
    () => [
      {
        accessor: "name",
        Cell: ({ row: { original } }) => <div data-test-id={original.dataTestId}>{original.name}</div>,
        style: {
          whiteSpace: "nowrap"
        }
      },
      {
        accessor: "value"
      }
    ],
    []
  );

  const expandedEventData = useMemo(() => {
    const event = events.find((e) => e.id === expanded);

    if (!event) {
      return [];
    }

    const eventDataRaw = [
      {
        name: <FormattedMessage id="date" />,
        dataTestId: "lbl_date",
        value: `${formatUTC(event.time, "MM/dd/yyyy hh:mm a")} UTC`
      },
      {
        name: <FormattedMessage id="objectName" />,
        dataTestId: "lbl_object_name",
        value: event.object_name
      },
      {
        name: <FormattedMessage id="objectType" />,
        dataTestId: "lbl_object_type",
        value: event.object_type
      },
      {
        name: <FormattedMessage id="description" />,
        dataTestId: "lbl_description",
        value: event.description
      }
    ];

    // adding resolve by at second row
    if (event.acknowledged_user) {
      eventDataRaw.splice(1, 0, {
        name: <FormattedMessage id="resolveBy" />,
        value: event.acknowledged_user
      });
    }

    return eventDataRaw;
  }, [events, expanded]);

  const getAccordionContent = (event) =>
    expanded === `${event.id}` ? (
      <Table
        data={expandedEventData}
        columns={eventTableColumns}
        localization={{ emptyMessageId: "noEvents" }}
        withHeader={false}
        dataTestIds={{
          container: "div_event_details"
        }}
      />
    ) : null;

  const renderAccordion = (eventsList, parentIndex) =>
    eventsList.map((event, index) => (
      <Accordion
        headerDataTestId={index === 0 && parentIndex === 0 ? "sp_first_event" : null}
        key={`${event.id}`}
        expanded={expanded === `${event.id}`}
        onChange={handleAccordion(`${event.id}`)}
        zeroSummaryMinHeight
        hideExpandIcon
      >
        <Typography variant="inherit" noWrap className={classes.heading}>
          {addIcon(event.level)}
          {event.description}
        </Typography>
        {getAccordionContent(event)}
      </Accordion>
    ));

  const getGroupedEvents = (eventsList) =>
    eventsList.reduce((resultObject, event) => {
      const groupKey = formatUTC(event.time);
      return {
        ...resultObject,
        [groupKey]: [...(resultObject[groupKey] || []), event]
      };
    }, {});

  const buildEventsBox = (eventsObj) =>
    Object.keys(eventsObj).map((groupKey, index) => (
      <Box key={groupKey} className={cx(index !== 0 && classes.dateBlock)}>
        <Typography>{groupKey}</Typography>
        {renderAccordion(eventsObj[groupKey], index)}
      </Box>
    ));

  const actionBarDefinition = {
    title: {
      messageId: "events",
      dataTestId: "lbl_events"
    }
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_1}>
          <Grid item xs={open ? 6 : 12} sm={open ? 7 : 12} md={open ? 9 : 12}>
            <Box className={classes.eventsWrapper}>
              {isLoading && isEmpty(events) ? (
                <Box className={cx(classes.events)}>
                  <Loader />
                </Box>
              ) : (
                <Box onScroll={onScroll} pl={0.5} className={cx(classes.events)}>
                  {buildEventsBox(getGroupedEvents(events))}
                  {isLoading ? <Loader /> : null}
                </Box>
              )}
            </Box>
          </Grid>
          {open ? (
            <Grid item xs={open ? 6 : 0} sm={open ? 5 : 0} md={open ? 3 : 0}>
              <EventsFilter open={open} handleDrawer={handleDrawer} applyFilter={applyFilter} />
            </Grid>
          ) : (
            <IconButton
              dataTestId="btn_op_filter"
              icon={<FilterListOutlinedIcon />}
              size="small"
              customClass={classes.button}
              onClick={handleDrawer}
              tooltip={{
                show: true,
                value: <FormattedMessage id="openFilter" />
              }}
            />
          )}
        </Grid>
      </PageContentWrapper>
    </>
  );
}

Events.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  onScroll: PropTypes.func.isRequired,
  applyFilter: PropTypes.func.isRequired,
  events: PropTypes.array.isRequired
};
