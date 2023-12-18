import PetsIcon from "@mui/icons-material/Pets";
import IconButton from "components/IconButton";
import OutlinedDiv from "components/OutlinedDiv";

export default {
  component: OutlinedDiv
};

export const basic = () => (
  <OutlinedDiv
    label="Label"
    endAdornment={<IconButton icon={<PetsIcon />} size="small" color="primary" edge="end" />}
    helperText="Helper text"
    multiline
  >
    <img src={`http://placekitten.com/${Math.round(200 - Math.random() * 100)}/${Math.round(200 - Math.random() * 100)}`} />
  </OutlinedDiv>
);
