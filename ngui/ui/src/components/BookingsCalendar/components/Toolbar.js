import React from "react";
import ChevronLeft from "@mui/icons-material/ChevronLeft";
import ChevronRight from "@mui/icons-material/ChevronRight";
import { ListItem, ListItemText } from "@mui/material";
import Typography from "@mui/material/Typography";
import { Navigate } from "react-big-calendar";
import ButtonGroup from "components/ButtonGroup";
import IconButton from "components/IconButton";
import useStyles from "../BookingsCalendar.styles";

const Toolbar = ({ onNavigate, onView, localizer, label, views, view }) => {
  const { classes } = useStyles();

  const { messages } = localizer;

  const getViewButtons = () => {
    const buttonsDefinition = views.map((viewName) => ({
      id: viewName,
      messageText: messages[viewName],
      action: () => onView(viewName)
    }));

    return (
      <ButtonGroup
        buttons={buttonsDefinition}
        activeButtonIndex={buttonsDefinition.indexOf(buttonsDefinition.find((button) => button.id === view))}
      />
    );
  };

  return (
    <div className={classes.toolbar}>
      <div className={classes.toolbarTodayButtonWrapper}>
        <ListItem button onClick={() => onNavigate(Navigate.TODAY)} className={classes.toolbarTodayButton}>
          <ListItemText>{messages.today}</ListItemText>
        </ListItem>
      </div>
      <div>
        <IconButton icon={<ChevronLeft />} onClick={() => onNavigate(Navigate.PREVIOUS)} />
        <IconButton icon={<ChevronRight />} onClick={() => onNavigate(Navigate.NEXT)} />
      </div>
      <div className={classes.toolbarDateTitle}>
        <Typography align="center">{label}</Typography>
      </div>
      {views.length > 1 && getViewButtons()}
    </div>
  );
};

export default Toolbar;
