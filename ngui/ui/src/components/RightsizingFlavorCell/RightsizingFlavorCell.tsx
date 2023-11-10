import CaptionedCell from "components/CaptionedCell";
import KeyValueLabel from "components/KeyValueLabel";

const RightsizingFlavorCell = ({ flavorName, flavorCpu }) => (
  <CaptionedCell
    caption={{
      node: <KeyValueLabel messageId="cpu" value={flavorCpu} isBoldValue={false} variant="caption" />
    }}
  >
    {flavorName}
  </CaptionedCell>
);

export default RightsizingFlavorCell;
