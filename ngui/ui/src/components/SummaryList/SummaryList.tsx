import { Box } from "@mui/material";
import IconButton from "components/IconButton";
import SubTitle from "components/SubTitle";
import TypographyLoader from "components/TypographyLoader";
import { isEmpty as isEmptyObject } from "utils/objects";

const SummaryList = ({ titleMessage, titleIconButton = {}, isLoading = false, items = [] }) => (
  <Box minWidth={isLoading ? "200px" : undefined}>
    <Box display="flex" alignItems="center" height="30px">
      <SubTitle>{titleMessage}</SubTitle>
      {isEmptyObject(titleIconButton) ? null : <IconButton {...titleIconButton} />}
    </Box>
    {isLoading ? <TypographyLoader linesCount={4} /> : <>{items}</>}
  </Box>
);

export default SummaryList;
