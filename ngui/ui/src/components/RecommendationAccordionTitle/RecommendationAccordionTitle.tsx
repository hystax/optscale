import { Fragment } from "react";
import { Divider, ListItemText } from "@mui/material";
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

export default RecommendationAccordionTitle;
