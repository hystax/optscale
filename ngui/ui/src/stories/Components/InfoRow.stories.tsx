import AccountTreeOutlinedIcon from "@mui/icons-material/AccountTreeOutlined";
import InfoRow from "components/InfoRow";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/InfoRow`
};

export const basic = () => <InfoRow title={"Cloud"} value={"Azure"} />;

export const withIcon = () => <InfoRow title={"Source Pool"} value={"Marketing"} icon={<AccountTreeOutlinedIcon />} />;
