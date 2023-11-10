import Tooltip from "components/Tooltip";
import { sliceByLimitWithEllipsis, sliceFromEndByLimitWithEllipsis } from "utils/strings";

const getText = (textToRender, externalRenderText) =>
  typeof externalRenderText === "function" ? externalRenderText(textToRender) : textToRender;

const SlicedText = ({ limit, text = "", externalRenderText, sliceFromEnd = false }) => {
  if (text && text.length > limit) {
    const shortText = sliceFromEnd ? sliceFromEndByLimitWithEllipsis(text, limit) : sliceByLimitWithEllipsis(text, limit);
    return (
      <Tooltip title={text} placement="top">
        <span>{getText(shortText, externalRenderText)}</span>
      </Tooltip>
    );
  }
  return getText(text, externalRenderText);
};

export default SlicedText;
