import Chip from "components/Chip";
import KeyValueLabel from "components/KeyValueLabel";

const MlRunsetTagForCreatedResourcesChip = ({ tagKey, tagValue }) => (
  <Chip
    key={tagValue}
    color="info"
    multiline
    label={
      <KeyValueLabel
        value={tagValue}
        text={tagKey}
        typographyProps={{
          keyStyle: {
            whiteSpace: "normal",
            wordBreak: "break-all"
          },
          valueStyle: {
            whiteSpace: "normal",
            wordBreak: "break-all"
          }
        }}
      />
    }
    variant="outlined"
    size="small"
  />
);

export default MlRunsetTagForCreatedResourcesChip;
