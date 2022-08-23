import { lighten } from "@mui/material/styles";

import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => {
  const SELECTED_EVENT_COLOR = theme.palette.primary.main;
  return {
    calendar: {
      "& .rbc-off-range-bg": {
        background: lighten(theme.palette.info.light, 0.9)
      },
      "& .rbc-off-range": {
        color: theme.palette.common.black
      },
      "& .rbc-today": {
        background: lighten(theme.palette.primary.main, 0.85)
      },
      "& .rbc-current-time-indicator": {
        backgroundColor: theme.palette.success.main
      },
      "& .rbc-show-more": {
        color: theme.palette.text.primary,
        backgroundColor: "inherit"
      },
      "& .rbc-event.rbc-selected, .rbc-day-slot .rbc-selected.rbc-background-event": {
        backgroundColor: SELECTED_EVENT_COLOR
      },
      "& .rbc-day-slot .rbc-event, .rbc-day-slot .rbc-background-event": {
        border: `1px solid ${theme.palette.common.white}`
      },
      "& .rbc-event, .rbc-day-slot .rbc-background-event": {
        borderRadius: "4px"
      }
    },
    event: {
      backgroundColor: theme.palette.info.main,
      color: theme.palette.common.white
    },
    selectedEvent: {
      backgroundColor: SELECTED_EVENT_COLOR
    },
    eventPopupWrapper: { width: "380px", height: "150px", padding: theme.spacing(2) },
    showMoreEventsPopupWrapper: {
      "& > *:not(:last-child)": {
        marginBottom: theme.spacing(0.25)
      },
      width: "250px",
      padding: theme.spacing(1)
    },
    toolbar: {
      display: "flex",
      marginBottom: theme.spacing(2),
      justifyContent: "center",
      alignItems: "center",
      flexWrap: "wrap"
    },
    toolbarDateTitle: {
      flexGrow: 1
    },
    toolbarTodayButtonWrapper: {
      marginRight: theme.spacing(1),
      display: "flex"
    },
    toolbarTodayButton: {
      width: "80px"
    }
  };
});

export default useStyles;
