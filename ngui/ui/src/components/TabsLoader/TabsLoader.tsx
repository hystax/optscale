import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";

const rowRender = (counter) =>
  [...Array(counter).keys()].map((x) => (
    <Box key={x} mr={1}>
      <Skeleton width={100} height={40} />
    </Box>
  ));

const TabsLoader = ({ tabsCount = 1 }) => (
  <>
    <Box width="100%" overflow="hidden" display="flex" mb={1}>
      {rowRender(tabsCount)}
    </Box>
    <Skeleton variant="rectangular" height={200} />
  </>
);

export default TabsLoader;
