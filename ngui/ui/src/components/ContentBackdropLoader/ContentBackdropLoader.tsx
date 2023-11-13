import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Backdrop from "components/Backdrop";

const ContentBackdropLoader = ({ isLoading = false, size, children }) => (
  <Box height="100%" position="relative">
    {isLoading && (
      <Backdrop customClass="contentLoader">
        <CircularProgress size={size} />
      </Backdrop>
    )}
    {children}
  </Box>
);

export default ContentBackdropLoader;
