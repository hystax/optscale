import { useEffect, useState, useMemo } from "react";
import ErrorIcon from "@mui/icons-material/Error";
import InfoIcon from "@mui/icons-material/Info";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import Accordion from "components/Accordion";
import ActionBar from "components/ActionBar";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import LinearSelector from "components/LinearSelector";
import PageContentWrapper from "components/PageContentWrapper";
import RangePickerForm from "components/RangePickerForm";
import Table from "components/Table";
import { useInitialMount } from "hooks/useInitialMount";
import { isEmpty } from "utils/arrays";
import { EVENT_LEVEL } from "utils/constants";
import { formatUTC } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";
import { getQueryParams, updateQueryParams, removeQueryParam } from "utils/network";
import useStyles from "./Events.styles";

const actionBarDefinition = {
  title: {
    messageId: "events",
    dataTestId: "lbl_events"
  }
};

const Loader = () => (
  <Box textAlign="center" pt={2}>
    <CircularProgress />
  </Box>
);

const Picker = ({ onApply }) => {
  const filterParams = getQueryParams();

  const initialStartDateValue = filterParams.timeStart ? Number(filterParams.timeStart) : null;
  const initialEndDateValue = filterParams.timeEnd ? Number(filterParams.timeEnd) : null;

  return (
    <RangePickerForm
      initialStartDateValue={initialStartDateValue}
      initialEndDateValue={initialEndDateValue}
      onApply={(startDate, endDate) =>
        onApply({
          timeStart: startDate,
          timeEnd: endDate
        })
      }
      notSetMessageId="latest"
      definedRanges={getBasicRangesSet()}
    />
  );
};

const EVENT_LEVEL_ITEMS = [
  {
    name: "all",
    value: EVENT_LEVEL.ALL,
    type: "text",
    dataTestId: "event_lvl_all"
  },
  {
    name: "info",
    value: EVENT_LEVEL.INFO,
    type: "text",
    dataTestId: "event_lvl_info"
  },
  {
    name: "warning",
    value: EVENT_LEVEL.WARNING,
    type: "text",
    dataTestId: "event_lvl_warning"
  },
  {
    name: "error",
    value: EVENT_LEVEL.ERROR,
    type: "text",
    dataTestId: "event_lvl_error"
  }
];

const DEFAULT_EVENT_LEVEL = EVENT_LEVEL_ITEMS.find(({ value: itemValue }) => itemValue === EVENT_LEVEL.ALL);

const EventLevelSelector = ({ eventLevel, onApply }) => {
  const getValue = () => {
    const { name, value } = EVENT_LEVEL_ITEMS.find(({ value: itemValue }) => eventLevel === itemValue) ?? DEFAULT_EVENT_LEVEL;

    return {
      name,
      value
    };
  };

  return (
    <LinearSelector
      value={getValue()}
      label={<FormattedMessage id="eventLevel" />}
      onChange={({ value }) =>
        onApply({
          level: value
        })
      }
      items={EVENT_LEVEL_ITEMS}
    />
  );
};

const Events = ({ eventLevel, onScroll, applyFilter, events, isLoading = false }) => {
  const [expanded, setExpanded] = useState("");
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
      [EVENT_LEVEL.INFO]: <InfoIcon className={cx(classes.tableIcon, classes.infoIcon)} />,
      [EVENT_LEVEL.WARNING]: <ErrorIcon className={cx(classes.tableIcon, classes.warningIcon)} />,
      [EVENT_LEVEL.ERROR]: <ErrorIcon color="error" className={classes.tableIcon} />
    })[level];

  const eventTableColumns = useMemo(
    () => [
      {
        accessorKey: "name",
        cell: ({ row: { original } }) => <div data-test-id={original.dataTestId}>{original.name}</div>,
        style: {
          whiteSpace: "nowrap"
        }
      },
      {
        accessorKey: "value"
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

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_1}>
          <Grid container item xs={12} direction="row" justifyContent="space-between">
            <Grid item>
              <EventLevelSelector eventLevel={eventLevel} onApply={applyFilter} />
            </Grid>
            <Grid item>
              <Picker onApply={applyFilter} />
            </Grid>
          </Grid>
          <Grid item xs={12}>
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
        </Grid>
      </PageContentWrapper>
    </>
  );
};

export default Events;
