import PushPinIcon from "@mui/icons-material/PushPin";
import { Typography } from "@mui/material";
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

export default Header;
