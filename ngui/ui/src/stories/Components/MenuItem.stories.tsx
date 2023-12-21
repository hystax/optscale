import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import MenuItem from "components/MenuItem";

export default {
  component: MenuItem
};

export const basic = () => (
  <MenuItem messageId="hystax">
    <ExitToAppOutlinedIcon />
  </MenuItem>
);

export const withOnclick = () => (
  <MenuItem messageId="hystax" onClick={() => console.log("IconMenuItem clicked")}>
    <ExitToAppOutlinedIcon />
  </MenuItem>
);
