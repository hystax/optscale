import React from "react";
import ArrowBackOutlinedIcon from "@mui/icons-material/ArrowBackOutlined";
import ArrowForwardOutlinedIcon from "@mui/icons-material/ArrowForwardOutlined";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import ReportProblemOutlinedIcon from "@mui/icons-material/ReportProblemOutlined";
import Avatar from "@mui/material/Avatar";
import ListItem from "@mui/material/ListItem";
import ListItemAvatar from "@mui/material/ListItemAvatar";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import {
  TASK_INCOMING_ASSIGNMENT_REQUESTS,
  TASK_OUTGOING_ASSIGNMENT_REQUESTS,
  TASK_EXCEEDED_POOLS,
  TASK_EXCEEDED_POOL_FORECASTS,
  TASK_VIOLATED_RESOURCE_CONSTRAINTS,
  TASK_VIOLATED_ORGANIZATION_CONSTRAINTS,
  TASK_DIVERGENT_CONSTRAINTS
} from "utils/constants";
import useStyles from "./TasksOverviewListItem.styles";

const TasksOverviewListItem = ({ count, type, text, dataTestId, button = true }) => {
  const { classes, cx } = useStyles();

  const getTaskIcon = (taskType) =>
    ({
      [TASK_INCOMING_ASSIGNMENT_REQUESTS]: (
        <ArrowBackOutlinedIcon className={cx(classes.avatarItem, classes.greenAvatarItem)} />
      ),
      [TASK_OUTGOING_ASSIGNMENT_REQUESTS]: (
        <ArrowForwardOutlinedIcon className={cx(classes.avatarItem, classes.greenAvatarItem)} />
      ),
      [TASK_EXCEEDED_POOLS]: <AttachMoneyIcon className={cx(classes.avatarItem, classes.redAvatarItem)} />,
      [TASK_EXCEEDED_POOL_FORECASTS]: <AttachMoneyIcon className={cx(classes.avatarItem, classes.yellowAvatarItem)} />,
      [TASK_VIOLATED_RESOURCE_CONSTRAINTS]: (
        <ErrorOutlineOutlinedIcon className={cx(classes.avatarItem, classes.redAvatarItem)} />
      ),
      [TASK_VIOLATED_ORGANIZATION_CONSTRAINTS]: (
        <ErrorOutlineOutlinedIcon className={cx(classes.avatarItem, classes.redAvatarItem)} />
      ),
      [TASK_DIVERGENT_CONSTRAINTS]: <ReportProblemOutlinedIcon className={cx(classes.avatarItem, classes.yellowAvatarItem)} />
    }[taskType]);

  return (
    <ListItem data-test-id={dataTestId} button={button} className={classes.listItem}>
      <ListItemAvatar className={classes.avatarWrapper}>
        {type ? <Avatar className={classes.avatar}>{getTaskIcon(type)}</Avatar> : null}
      </ListItemAvatar>
      <ListItemText
        primary={
          <>
            <Typography className={classes.name}>
              {type ? (
                <FormattedMessage
                  id={`${type}`}
                  values={{
                    count
                  }}
                />
              ) : null}
            </Typography>{" "}
            <Typography className={classes.text}>{text}</Typography>
          </>
        }
      />
    </ListItem>
  );
};

TasksOverviewListItem.propTypes = {
  count: PropTypes.number.isRequired,
  type: PropTypes.string.isRequired,
  dataTestId: PropTypes.string,
  text: PropTypes.string,
  button: PropTypes.bool
};

export default TasksOverviewListItem;
