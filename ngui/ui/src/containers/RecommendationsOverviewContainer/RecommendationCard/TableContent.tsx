import { Typography } from "@mui/material";
import useStyles from "./TableContent.styles";

const TableContent = ({ data }) => {
  // TODO: Handle 0 items count
  const columnsCount = data[0]?.length ?? 0;
  const { classes } = useStyles(columnsCount);
  return (
    <Typography component="div" className={classes.grid}>
      {data.flat().map(({ key, value }) => (
        <div key={key}>{value}</div>
      ))}
    </Typography>
  );
};

export default TableContent;
