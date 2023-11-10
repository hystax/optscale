import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";

const TypographyLoader = ({ linesCount = 1 }) =>
  [...Array(linesCount).keys()].map((line) => (
    <Typography key={line}>
      <Skeleton />
    </Typography>
  ));

export default TypographyLoader;
