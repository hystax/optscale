import Checkbox from "@mui/material/Checkbox";
import Skeleton from "components/Skeleton";

const CheckboxLoader = ({ fullWidth = false }) => (
  <Skeleton type="rect" fullWidth={fullWidth}>
    <Checkbox />
  </Skeleton>
);

export default CheckboxLoader;
