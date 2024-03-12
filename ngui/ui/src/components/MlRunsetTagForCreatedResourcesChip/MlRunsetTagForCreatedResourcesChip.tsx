import Chip from "components/Chip";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";

const MlRunsetTagForCreatedResourcesChip = ({ tagKey, tagValue }) => (
  <Chip
    key={tagValue}
    color="info"
    multiline
    label={<KeyValueLabel value={tagValue} keyText={tagKey} />}
    variant="outlined"
    size="small"
  />
);

export default MlRunsetTagForCreatedResourcesChip;
