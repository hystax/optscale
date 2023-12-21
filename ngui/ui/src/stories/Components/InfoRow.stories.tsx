import AccountTreeOutlinedIcon from "@mui/icons-material/AccountTreeOutlined";
import InfoRow from "components/InfoRow";

export default {
  component: InfoRow
};

export const basic = () => <InfoRow title={"Cloud"} value={"Azure"} />;

export const withIcon = () => <InfoRow title={"Source Pool"} value={"Marketing"} icon={<AccountTreeOutlinedIcon />} />;
