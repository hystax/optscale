import MuiChip from "@mui/material/Chip";
import { useTheme } from "@mui/material/styles";
import SlicedText from "components/SlicedText";
import { getHash } from "utils/strings";

function calculateColorFromString(inputString) {
  const hash = getHash(inputString);

  // Use bitwise AND to ensure the values are between 0 and 255
  const r = (hash & 0xff0000) >> 16; // (0x123456 & 0xff0000) >> 16 => 0x120000 >> 16 => 0x12 => 18
  const g = (hash & 0x00ff00) >> 8;
  const b = hash & 0x0000ff;

  return { r, g, b };
}

const LABEL_SYMBOLS_LIMIT = 20;

const LabelChip = ({ label }) => {
  const theme = useTheme();
  const {
    palette: { getContrastText }
  } = theme;

  const { r, g, b } = calculateColorFromString(label);

  const rgbColor = `rgb(${r},${g},${b})`;

  return (
    <MuiChip
      variant="outlined"
      label={<SlicedText limit={LABEL_SYMBOLS_LIMIT} text={label} />}
      sx={{
        color: getContrastText(rgbColor),
        backgroundColor: rgbColor,
        borderColor: rgbColor
      }}
      size="small"
    />
  );
};

export default LabelChip;
