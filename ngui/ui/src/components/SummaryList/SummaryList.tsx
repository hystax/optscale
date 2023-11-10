import IconButton from "components/IconButton";
import SubTitle from "components/SubTitle";
import TypographyLoader from "components/TypographyLoader";
import { isEmpty as isEmptyObject } from "utils/objects";

const SummaryList = ({ titleMessage, titleIconButton = {}, isLoading = false, items = [] }) => (
  <div>
    <div
      style={{
        display: "flex",
        alignItems: "center",
        height: "30px"
      }}
    >
      <SubTitle>{titleMessage}</SubTitle>
      {isEmptyObject(titleIconButton) ? null : <IconButton {...titleIconButton} />}
    </div>
    {isLoading ? <TypographyLoader linesCount={4} /> : <>{items}</>}
  </div>
);

export default SummaryList;
