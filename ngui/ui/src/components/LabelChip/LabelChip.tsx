import { Typography, type TypographyProps } from "@mui/material";
import MuiChip from "@mui/material/Chip";
import { useTheme } from "@mui/material/styles";
import SlicedText from "components/SlicedText";
import { getHash } from "utils/strings";

type LabelChipProps = {
  label: string;
  colorizeBy?: string;
  labelSymbolsLimit?: number;
  labelTypographyProps?: TypographyProps;
};

const calculateColorFromString = (inputString: string) => {
  const hash = getHash(inputString);

  // Use bitwise AND to ensure the values are between 0 and 255
  const r = (hash & 0xff0000) >> 16; // (0x123456 & 0xff0000) >> 16 => 0x120000 >> 16 => 0x12 => 18
  const g = (hash & 0x00ff00) >> 8;
  const b = hash & 0x0000ff;

  return { r, g, b };
};

const DEFAULT_LABEL_SYMBOLS_LIMIT = 20;

const LabelChip = ({
  label,
  colorizeBy = label,
  labelSymbolsLimit = DEFAULT_LABEL_SYMBOLS_LIMIT,
  labelTypographyProps
}: LabelChipProps) => {
  const theme = useTheme();
  const {
    palette: { getContrastText }
  } = theme;

  const { r, g, b } = calculateColorFromString(colorizeBy);

  const rgbColor = `rgb(${r},${g},${b})`;

  return (
    <MuiChip
      variant="outlined"
      label={
        <Typography {...labelTypographyProps}>
          <SlicedText limit={labelSymbolsLimit} text={label} />
        </Typography>
      }
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
