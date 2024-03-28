import Tooltip from "components/Tooltip";
import { sliceByLimitWithEllipsis, sliceFromEndByLimitWithEllipsis } from "utils/strings";

type SlicedTextProps = {
  limit: number;
  text: string;
  sliceFromEnd?: boolean;
};

const SlicedText = ({ limit, text = "", sliceFromEnd = false }: SlicedTextProps) => {
  if (text && text.length > limit) {
    const shortText = sliceFromEnd ? sliceFromEndByLimitWithEllipsis(text, limit) : sliceByLimitWithEllipsis(text, limit);
    return (
      <Tooltip title={text} placement="top">
        <span>{shortText}</span>
      </Tooltip>
    );
  }
  return text;
};

export default SlicedText;
