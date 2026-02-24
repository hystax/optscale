import RocketLaunchOutlinedIcon from "@mui/icons-material/RocketLaunchOutlined";
import Button from "components/Button";
import { CONTACT_US_URL } from "urls";

const UpgradeToEnterpriseButton = () => (
  <Button
    fullWidth
    messageId="upgradeToEnterprise"
    color="primary"
    variant="contained"
    href={CONTACT_US_URL}
    startIcon={<RocketLaunchOutlinedIcon />}
    sx={{
      whiteSpace: "nowrap",
    }}
  />
);

export default UpgradeToEnterpriseButton;
