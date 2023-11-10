import Switch from "@mui/material/Switch";
import Skeleton from "components/Skeleton";

const SwitchLoader = ({ fullWidth = false }) => (
  <Skeleton type="rect" fullWidth={fullWidth}>
    <Switch />
  </Skeleton>
);

export default SwitchLoader;
