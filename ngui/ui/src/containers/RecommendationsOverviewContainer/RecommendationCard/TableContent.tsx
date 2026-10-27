import { Box, Typography } from "@mui/material";
import useStyles from "./TableContent.styles";

type TableContentProps = {
  data: { key: string; value: string }[][];
};

const TableContent = ({ data }: TableContentProps) => {
  const columnsCount = data[0]?.length ?? 0;
  const { classes } = useStyles({ columnsCount });
  return (
    <Typography component="div" className={classes.grid}>
      {data.flat().map(({ key, value }) => (
        <Box
          key={key}
          sx={{
            "& > div": {
              height: "100%",
            },
          }}
        >
          {value}
        </Box>
      ))}
    </Typography>
  );
};

export default TableContent;
