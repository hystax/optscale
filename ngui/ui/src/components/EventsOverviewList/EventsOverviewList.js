import React from "react";
import { Box, Typography, Container } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";
import Link from "@mui/material/Link";
import List from "@mui/material/List";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import EventsOverviewListItem from "components/EventsOverviewListItem";
import { EVENTS } from "urls";
import { isEmpty } from "utils/arrays";
import { getCurrentTimeInMsec } from "utils/datetime";
import useStyles from "./EventsOverviewList.styles";

const EventsOverviewList = ({ events, isLoading }) => {
  const { classes } = useStyles();

  const renderLatestEvents = () =>
    !isEmpty(events) ? (
      <List component="nav" aria-labelledby="nested-list-subheader" className={classes.listContainer}>
        {events.map((event) => (
          <Link
            className={classes.buttonLink}
            to={`${EVENTS}?event=${event.id}`}
            component={RouterLink}
            key={`event${event.id}`}
          >
            <EventsOverviewListItem
              key={event.id}
              title={event.object_name || ""}
              description={event.description || ""}
              time={event.time || getCurrentTimeInMsec()}
              level={event.level}
            />
          </Link>
        ))}
      </List>
    ) : (
      <List>
        <Container className={classes.customContainer} maxWidth="sm">
          <Typography display="block" gutterBottom>
            {<FormattedMessage id="youHaveNoEvents" />}
          </Typography>
        </Container>
      </List>
    );

  return (
    <Box className={classes.wrapper}>
      {isLoading ? (
        <Box margin="auto" width="fit-content">
          <CircularProgress />
        </Box>
      ) : (
        renderLatestEvents()
      )}
    </Box>
  );
};

EventsOverviewList.propTypes = {
  events: PropTypes.array.isRequired,
  isLoading: PropTypes.bool.isRequired
};

export default EventsOverviewList;
