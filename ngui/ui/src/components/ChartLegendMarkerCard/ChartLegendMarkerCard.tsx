import { Typography } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import useStyles from "components/ChartLegendMarkerCard/ChartLegendMarkerCard.styles";
import TitleValue from "components/TitleValue";

const Body = ({ color: markerColor, title = "", value = "", dataTestIds = {} }) => {
  const { classes, cx } = useStyles({ markerColor });

  const { title: titleDataTestId, value: valueDataTestId } = dataTestIds;

  return (
    <div className={classes.wrapper}>
      <div className={cx(classes.marker, classes.markerColor)} />
      <div className={classes.content}>
        <Typography color="textSecondary" variant="caption" data-test-id={titleDataTestId}>
          {title}
        </Typography>
        <TitleValue dataTestId={valueDataTestId}>{value}</TitleValue>
      </div>
    </div>
  );
};

const ChartLegendMarkerCard = ({ isLoading = false, ...rest }) => {
  const body = <Body {...rest} />;
  return isLoading ? (
    <Skeleton variant="rectangular" width="100px">
      {body}
    </Skeleton>
  ) : (
    body
  );
};

export default ChartLegendMarkerCard;
