import React from "react";
import { Box } from "@mui/material";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { getTimeDistance } from "utils/datetime";
import { sliceByLimitWithEllipsis } from "utils/strings";
import useStyles from "./EventsOverviewListItem.styles";

const EventsOverviewListItem = (props) => {
  const { classes } = useStyles();
  const { title, description, time, level = "info", isButton = true } = props;

  return (
    <ListItem button={isButton} className={classes.listItem}>
      <ListItemText
        primary={
          <Box display="flex">
            <Box className={classes[level.toString().toLowerCase()] || classes.info} ml={-2}>
              <div className={classes.level} />
            </Box>
            <Box pl={1} fontWeight={"fontWeightBold"}>
              <Typography className={classes.title}>{title}</Typography>
              <Typography className={classes.description}>{sliceByLimitWithEllipsis(description, 350)}</Typography>
              <Typography className={classes.timeAgo}>
                <FormattedMessage
                  id="valueAgo"
                  values={{
                    value: getTimeDistance(time)
                  }}
                />
              </Typography>
            </Box>
          </Box>
        }
      />
    </ListItem>
  );
};

EventsOverviewListItem.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  time: PropTypes.number.isRequired,
  level: PropTypes.string,
  isButton: PropTypes.bool
};

export default EventsOverviewListItem;
