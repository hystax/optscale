import BusinessIcon from "@mui/icons-material/Business";
import CloudIcon from "@mui/icons-material/Cloud";
import PeopleIcon from "@mui/icons-material/People";
import ButtonSwitch from "components/ButtonSwitch";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ButtonSwitch`
};

const buttons = [
  { messageId: "cloud", link: "/", icon: <CloudIcon /> },
  { messageId: "pool", link: "/", icon: <BusinessIcon /> },
  { messageId: "owner", link: "/", icon: <PeopleIcon /> }
];

export const basic = () => <ButtonSwitch buttons={buttons} />;
