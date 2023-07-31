import React from "react";
import { Box } from "@mui/material";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Checkbox from "@mui/material/Checkbox";
import Collapse from "@mui/material/Collapse";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import SubTitle from "components/SubTitle";
import { useToggle } from "hooks/useToggle";
import useStyles from "./ChecklistCard.styles";

const ChecklistCard = ({ title, description, checked, canUpdate, onClick, dataTestId, image }) => {
  const { classes, cx } = useStyles();

  const [isExpanded, setIsExpanded] = useToggle(false);

  return (
    <Card
      className={cx(classes.root, {
        [classes.fullHeight]: isExpanded
      })}
    >
      <CardHeader action={<Checkbox data-test-id={dataTestId} checked={checked} disabled={!canUpdate} onClick={onClick} />} />
      <CardContent className={classes.illustrationContainer}>
        <img src={image} alt="" className={cx(classes.illustration, !checked && classes.blackAndWhite)} />
      </CardContent>
      <CardActions
        classes={{
          root: classes.title
        }}
      >
        <Box display="inline" className={classes.titleContainer}>
          <SubTitle onClick={setIsExpanded} className={classes.subtitle}>
            {title}
          </SubTitle>
        </Box>
      </CardActions>
      <Collapse in={isExpanded} timeout="auto" unmountOnExit>
        <CardContent>
          <Typography className={classes.descriptionContainer}>{description}</Typography>
        </CardContent>
      </Collapse>
    </Card>
  );
};

ChecklistCard.propTypes = {
  title: PropTypes.oneOfType([PropTypes.string, PropTypes.node]).isRequired,
  description: PropTypes.oneOfType([PropTypes.string, PropTypes.node]).isRequired,
  checked: PropTypes.bool.isRequired,
  canUpdate: PropTypes.bool.isRequired,
  onClick: PropTypes.func.isRequired,
  dataTestId: PropTypes.string.isRequired,
  image: PropTypes.any
};

export default ChecklistCard;
