import React from "react";
import { Paper, lighten } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import IconLabel from "components/IconLabel";
import SubTitle from "components/SubTitle";
import TitleValue from "components/TitleValue";
import useStyles from "./InfoCard.styles";

const InfoCard = ({ title, value, isLoading, dataTestIds = {}, icon, color }) => {
  const { classes } = useStyles();

  const { title: titleDataTestId, value: valueDataTestId } = dataTestIds;

  const body = (
    <Paper
      elevation={0}
      className={classes.infoCard}
      sx={{
        backgroundColor: color ? (theme) => lighten(theme.palette[color].main, 0.95) : undefined
      }}
    >
      <IconLabel
        icon={icon}
        label={
          <SubTitle
            align="center"
            data-test-id={titleDataTestId}
            sx={{
              ml: 1
            }}
          >
            {title}
          </SubTitle>
        }
      />
      <TitleValue dataTestId={valueDataTestId}>{value}</TitleValue>
    </Paper>
  );

  return isLoading ? (
    <Skeleton width="100%" variant="rectangular">
      {body}
    </Skeleton>
  ) : (
    body
  );
};

export default InfoCard;
