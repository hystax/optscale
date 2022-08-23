import React, { Fragment } from "react";
import { Divider, ListItemText } from "@mui/material";
import PropTypes from "prop-types";
import useStyles from "./RecommendationAccordionTitle.styles";

const RecommendationAccordionTitle = ({ messages = [] }) => {
  const { classes } = useStyles();

  return (
    <ListItemText
      primaryTypographyProps={{
        variant: "body2",
        className: classes.text
      }}
      primary={messages.map((message, index) => (
        <Fragment key={message.key}>
          {message}
          {index !== messages.length - 1 && (
            <Divider
              orientation="vertical"
              flexItem
              classes={{
                root: classes.divider
              }}
            />
          )}
        </Fragment>
      ))}
    />
  );
};

RecommendationAccordionTitle.propTypes = {
  messages: PropTypes.arrayOf(PropTypes.node)
};

export default RecommendationAccordionTitle;
