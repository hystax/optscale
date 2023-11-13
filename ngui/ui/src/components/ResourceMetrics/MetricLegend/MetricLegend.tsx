import { Grid } from "@mui/material";
import ChartLegendMarkerCard from "components/ChartLegendMarkerCard";
import { SPACING_2 } from "utils/layouts";

const renderLegendGridItems = (legend) =>
  legend.map((marker) => (
    <Grid item key={marker.name}>
      <ChartLegendMarkerCard title={marker.title} value={marker.value} color={marker.color} dataTestIds={marker.dataTestIds} />
    </Grid>
  ));

const MetricLegend = ({ legend = [], isLoading }) => (
  <Grid container spacing={SPACING_2}>
    {isLoading ? (
      <Grid item>
        <ChartLegendMarkerCard isLoading />
      </Grid>
    ) : (
      renderLegendGridItems(legend)
    )}
  </Grid>
);

export default MetricLegend;
