import Box from "@mui/material/Box";
import MuiPagination from "@mui/material/Pagination";
import PaginationItem from "@mui/material/PaginationItem";
import useStyles from "./Pagination.styles";

const Pagination = ({ count, paginationHandler, position = "right", page = 1 }) => {
  const { classes, cx } = useStyles();

  const wrapperClasses = cx(classes.wrapper, classes[position]);

  return (
    <Box className={wrapperClasses}>
      <MuiPagination
        renderItem={({ type, page: pageNum, ...rest }) => {
          const itemId = type !== "previous" && type !== "next" ? `${pageNum}` : type;
          return <PaginationItem data-test-id={`btn_pagination_${itemId}`} page={pageNum} type={type} {...rest} />;
        }}
        page={page}
        count={count}
        onChange={(_, newPage) => {
          const newPageIndex = newPage - 1;

          return paginationHandler(newPageIndex);
        }}
      />
    </Box>
  );
};

export default Pagination;
