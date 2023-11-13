import { ListItem, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import useStyles from "./MainMenuSectionTitle.styles";

const MainMenuSectionTitle = ({ messageId }) => {
  const { classes } = useStyles();

  return (
    <ListItem className={classes.textWrapper}>
      <Typography variant="caption" className={classes.text}>
        <FormattedMessage id={messageId} />
      </Typography>
    </ListItem>
  );
};

export default MainMenuSectionTitle;
