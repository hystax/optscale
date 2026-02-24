import { FormControl, InputLabel, MenuItem, OutlinedInput, Select } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { CATEGORY } from "../recommendations/BaseRecommendation";

export const RECOMMENDATIONS_FILTERS = Object.freeze([
  { messageId: "all", id: CATEGORY.ALL },
  { messageId: "savings", id: CATEGORY.COST },
  { messageId: "security", id: CATEGORY.SECURITY },
  { messageId: "critical", id: CATEGORY.CRITICAL },
  { messageId: "nonEmpty", id: CATEGORY.NON_EMPTY },
]);

export const POSSIBLE_RECOMMENDATIONS_FILTERS = RECOMMENDATIONS_FILTERS.map(({ id }) => id);

export const DEFAULT_RECOMMENDATIONS_FILTER = RECOMMENDATIONS_FILTERS[0].id;

const RecommendationsFilter = ({ onChange, value }) => {
  const intl = useIntl();
  const label = intl.formatMessage({ id: "categories" });

  return (
    <FormControl sx={{ minWidth: "250px" }}>
      <InputLabel id="services-label">{label}</InputLabel>
      <Select
        labelId="services-label"
        id="services"
        value={value}
        onChange={({ target: { value: newValue } }) => onChange(newValue)}
        input={<OutlinedInput label={label} />}
        renderValue={(selected) => (
          <FormattedMessage id={RECOMMENDATIONS_FILTERS.find(({ id }) => id === selected).messageId} />
        )}
      >
        {RECOMMENDATIONS_FILTERS.map(({ messageId, id }) => (
          <MenuItem key={id} value={id}>
            <FormattedMessage id={messageId} />
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default RecommendationsFilter;
