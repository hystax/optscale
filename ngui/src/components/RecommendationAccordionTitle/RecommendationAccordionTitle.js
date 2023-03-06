import React, { Fragment } from "react";
import { Divider, ListItemText } from "@mui/material";
import PropTypes from "prop-types";
import useStyles from "./RecommendationAccordionTitle.styles";

const RecommendationAccordionTitle = ({ messages = [], dataTestId }) => {
  const { classes } = useStyles();

  return (
    <ListItemText
      primaryTypographyProps={{
        variant: "body2",
        component: "span",
        className: classes.text,
        "data-test-id": dataTestId
      }}
      primary={messages.map((message, index) => (
        <Fragment key={message.key}>
          {message}
          {index !== messages.length - 1 && (
            <Divider
              component="span"
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
  messages: PropTypes.arrayOf(PropTypes.node),
  dataTestId: PropTypes.string
};

export default RecommendationAccordionTitle;
