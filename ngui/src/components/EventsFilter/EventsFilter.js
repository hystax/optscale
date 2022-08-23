import React from "react";
import CloseIcon from "@mui/icons-material/Close";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import EventsFilterForm from "components/EventsFilterForm";
import IconButton from "components/IconButton";
import WrapperCard from "components/WrapperCard";
import useStyles from "./EventsFilter.styles";

const EventsFilter = ({ open, handleDrawer, applyFilter }) => {
  const { classes, cx } = useStyles();

  const onFormSubmit = ({ level, timeStart, timeEnd }) => {
    applyFilter({
      level,
      timeStart,
      timeEnd
    });
  };

  return (
    <WrapperCard
      title={
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <FormattedMessage id="filter" />
          <IconButton
            dataTestId="btn_cl_filter"
            icon={<CloseIcon />}
            onClick={handleDrawer}
            tooltip={{
              show: true,
              value: <FormattedMessage id="closeFilter" />
            }}
          />
        </Box>
      }
    >
      <Drawer
        anchor="right"
        variant="persistent"
        classes={{
          paper: cx(classes.drawerPaper, !open && classes.drawerPaperClose)
        }}
        open={open}
      >
        <EventsFilterForm onSubmit={onFormSubmit} />
      </Drawer>
    </WrapperCard>
  );
};

EventsFilter.propTypes = {
  open: PropTypes.bool.isRequired,
  handleDrawer: PropTypes.func.isRequired,
  applyFilter: PropTypes.func.isRequired
};
export default EventsFilter;
