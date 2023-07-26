import React from "react";
import { FormControl, InputLabel, MenuItem, OutlinedInput, Select } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import { CATEGORY_COST, CATEGORY_SECURITY } from "../recommendations/BaseRecommendation";

const CATEGORY_ALL = "all";
const CATEGORY_CRITICAL = "critical";
const CATEGORY_NON_EMPTY = "nonEmpty";

export const RECOMMENDATIONS_FILTERS = Object.freeze([
  { messageId: "all", id: CATEGORY_ALL },
  { messageId: "savings", id: CATEGORY_COST },
  { messageId: "security", id: CATEGORY_SECURITY },
  { messageId: "critical", id: CATEGORY_CRITICAL },
  { messageId: "nonEmpty", id: CATEGORY_NON_EMPTY }
]);

export const POSSIBLE_RECOMMENDATIONS_FILTERS = RECOMMENDATIONS_FILTERS.map(({ id }) => id);

export const DEFAULT_RECOMMENDATIONS_FILTER = RECOMMENDATIONS_FILTERS[0].id;

export const categoryFilter = (category) => (recommendation) => {
  if (category === CATEGORY_ALL) {
    return true;
  }

  // two definitional categories
  if ([CATEGORY_COST, CATEGORY_SECURITY].includes(category)) {
    return recommendation.categories.includes(category);
  }

  if (category === CATEGORY_CRITICAL) {
    return recommendation.color === "error";
  }

  if (category === CATEGORY_NON_EMPTY) {
    return recommendation.saving !== 0 && recommendation.count !== 0;
  }

  return true;
};

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

RecommendationsFilter.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired
};

export default RecommendationsFilter;
