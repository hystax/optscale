import CaptionedCell from "components/CaptionedCell";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";

const RightsizingFlavorCell = ({ flavorName, flavorCpu }) => (
  <CaptionedCell
    caption={{
      node: <KeyValueLabel keyMessageId="cpu" value={flavorCpu} isBoldValue={false} variant="caption" />
    }}
  >
    {flavorName}
  </CaptionedCell>
);

export default RightsizingFlavorCell;
