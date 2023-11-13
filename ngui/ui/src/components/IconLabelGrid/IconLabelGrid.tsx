import Grid from "@mui/material/Grid";
import { SPACING_1 } from "utils/layouts";

const IconLabelGrid = ({ startIcon, label, endIcon }) => (
  <Grid container spacing={SPACING_1} alignItems="center" wrap="nowrap">
    {startIcon}
    <Grid item>{label}</Grid>
    {endIcon}
  </Grid>
);

export default IconLabelGrid;
