import React from "react";
import NotificationsIcon from "@mui/icons-material/Notifications";
import Badge from "@mui/material/Badge";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import Popover from "components/Popover";
import WrapperCard from "components/WrapperCard";
import EventsOverviewListContainer from "containers/EventsOverviewListContainer";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import useStyles from "./LatestEvents.styles";

const LatestEvents = ({ count = 0 }) => {
  const { classes } = useStyles();
  const isUpMd = useIsUpMediaQuery("md");
  return (
    <Popover
      label={
        <IconButton
          icon={
            <Badge badgeContent={count} color="error">
              <NotificationsIcon size="large" />
            </Badge>
          }
          size={isUpMd ? "small" : "medium"}
          color="primary"
          customClass={classes.button}
          tooltip={{
            show: true,
            value: <FormattedMessage id="events" />
          }}
        />
      }
      menu={
        <WrapperCard title={<FormattedMessage id="events" />} button={{ show: true, messageId: "goToEvents", link: "/events" }}>
          <EventsOverviewListContainer />
        </WrapperCard>
      }
    />
  );
};

LatestEvents.propTypes = {
  count: PropTypes.number.isRequired
};

export default LatestEvents;
