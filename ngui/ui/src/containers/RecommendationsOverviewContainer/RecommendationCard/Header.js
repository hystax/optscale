import React from "react";
import PushPinIcon from "@mui/icons-material/PushPin";
import { Typography } from "@mui/material";
import PropTypes from "prop-types";
import SubTitle from "components/SubTitle";
import TitleValue from "components/TitleValue";
import { useIsRecommendationPinned } from "../redux/pinnedRecommendations/hooks";
import useStyles from "./Header.styles";

const Header = ({ recommendationType, color, title, subtitle, value, valueLabel }) => {
  const { classes } = useStyles();

  const isPinned = useIsRecommendationPinned(recommendationType);

  return (
    <div className={classes.header}>
      <div className={classes.title}>
        <div className={classes.titleText}>
          <TitleValue component="h3">{title}</TitleValue>
          {isPinned && (
            <PushPinIcon
              style={{
                marginTop: "4px",
                transform: "rotate(45deg)"
              }}
              fontSize="small"
            />
          )}
        </div>
        <SubTitle>{subtitle}</SubTitle>
      </div>
      <div className={classes.value}>
        <Typography variant="h6" component="div" color={color} fontWeight="bold">
          {value}
        </Typography>
        <Typography variant="body2" component="div" fontWeight="bold" color={color}>
          {valueLabel}
        </Typography>
      </div>
    </div>
  );
};

Header.propTypes = {
  recommendationType: PropTypes.string,
  color: PropTypes.oneOf(["primary", "secondary", "success", "error", "warning"]),
  title: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  subtitle: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  valueLabel: PropTypes.oneOfType([PropTypes.string, PropTypes.node])
};

export default Header;
