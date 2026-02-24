import { MouseEvent, ReactNode, useMemo, useState } from "react";
import LightbulbOutlinedIcon from "@mui/icons-material/LightbulbOutlined";
import { Box, Button, Popover, Typography, Checkbox, FormControlLabel, FormGroup } from "@mui/material";
import Divider from "@mui/material/Divider";
import { FormattedMessage } from "react-intl";
import { isEmptyArray, isLastItem } from "utils/arrays";

export type FilterItem = {
  value: string;
  name: string;
  [key: string]: unknown;
};

export type SuggestionGroup = {
  id: string;
  title: ReactNode;
  items: FilterItem[];
  renderItem: (item: FilterItem) => ReactNode;
};

type SuggestionStateButtonProps = {
  onClick: (event: MouseEvent<HTMLButtonElement>) => void;
  id?: string;
  label: ReactNode;
};

const SuggestionStateButton = ({ onClick, id, label }: SuggestionStateButtonProps) => (
  <Button aria-describedby={id} variant="outlined" onClick={onClick} color="primary" startIcon={<LightbulbOutlinedIcon />}>
    {label}
  </Button>
);

type SuggestionFilterProps = {
  suggestionGroups: SuggestionGroup[];
  label: ReactNode;
  onApplySuggestion: (updates: Record<string, string[]>) => void;
  appliedFilters: Record<string, string[]>;
};

const SuggestionFilter = ({ suggestionGroups, label, onApplySuggestion, appliedFilters }: SuggestionFilterProps) => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const [selectedSuggestions, setSelectedSuggestions] = useState<Record<string, string[]>>(
    Object.fromEntries(suggestionGroups.map((group) => [group.id, []]))
  );

  const onOpen = (event: MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);

    setSelectedSuggestions(
      Object.fromEntries(
        suggestionGroups.map((group) => {
          const values = group.items.filter((item) => appliedFilters[group.id].includes(item.value)).map((item) => item.value);

          return [group.id, values];
        })
      )
    );
  };

  const handleCancel = () => {
    setAnchorEl(null);
    // Reset selections to what they were when opened
    setSelectedSuggestions(
      Object.fromEntries(
        suggestionGroups.map((group) => {
          const values = group.items.filter((item) => appliedFilters[group.id].includes(item.value)).map((item) => item.value);

          return [group.id, values];
        })
      )
    );
  };

  const handleApply = () => {
    const updates = Object.fromEntries(
      Object.entries(selectedSuggestions).map(([type, selectedValues]) => {
        const suggestedValues = suggestionGroups.find((g) => g.id === type)?.items.map((item) => item.value) ?? [];
        const nonSuggestedValues = appliedFilters[type].filter((item) => !suggestedValues.includes(item));

        return [
          type,
          // Keep non-suggested values and add selected suggested values
          [...nonSuggestedValues, ...selectedValues],
        ];
      })
    );

    onApplySuggestion(updates);
    setAnchorEl(null);
  };

  const handleSuggestionToggle = (suggestion: string, groupId: string) => {
    setSelectedSuggestions((prev) => {
      const currentValues = prev[groupId];

      return {
        ...prev,
        [groupId]: currentValues.includes(suggestion)
          ? currentValues.filter((item) => item !== suggestion)
          : [...currentValues, suggestion],
      };
    });
  };

  const open = Boolean(anchorEl);
  const id = open ? "suggestion-filter-popover" : undefined;

  // Check if there are any changes in selections compared to applied filters
  const hasChanges = useMemo(
    () =>
      Object.entries(selectedSuggestions).some(([groupId, values]) => {
        const appliedValues = appliedFilters[groupId] || [];
        // Check if arrays have different values by comparing stringified versions
        return JSON.stringify(values.sort()) !== JSON.stringify(appliedValues.sort());
      }),
    [selectedSuggestions, appliedFilters]
  );

  // Check if there are any suggestions available
  const hasSuggestions = suggestionGroups.some((group) => !isEmptyArray(group.items));

  return (
    <div>
      <SuggestionStateButton onClick={onOpen} id={id} label={label} />
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleCancel}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
      >
        <Box sx={{ display: "flex", flexDirection: "column", width: "350px" }}>
          <Box sx={{ maxHeight: "400px", overflowY: "auto", overflowX: "hidden", pt: 2 }}>
            {hasSuggestions ? (
              suggestionGroups
                .filter((group) => !isEmptyArray(group.items))
                .map((group, groupIndex, sourceArray) => (
                  <Box key={group.id}>
                    <Typography variant="subtitle2" color="primary" sx={{ px: 2, fontWeight: "bold" }}>
                      {group.title}
                    </Typography>
                    <FormGroup>
                      {group.items.map((suggestion) => (
                        <Box key={`${group.id}-${suggestion.value}`}>
                          <FormControlLabel
                            control={
                              <Checkbox
                                checked={selectedSuggestions[group.id].some((value) => value === suggestion.value)}
                                onChange={() => handleSuggestionToggle(suggestion.value, group.id)}
                              />
                            }
                            label={
                              <Typography variant="body2">
                                {group.renderItem ? group.renderItem(suggestion) : suggestion.value}
                              </Typography>
                            }
                            sx={{ px: 2, width: "100%" }}
                          />
                        </Box>
                      ))}
                    </FormGroup>
                    {isLastItem(groupIndex, sourceArray.length) ? null : <Divider sx={{ my: 1 }} />}
                  </Box>
                ))
            ) : (
              <Typography variant="body2" sx={{ textAlign: "center", py: 1 }}>
                <FormattedMessage id="noSuggestionsAvailable" />
              </Typography>
            )}
          </Box>
          <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1, px: 2, py: 1, borderTop: 1, borderColor: "divider" }}>
            <Button onClick={handleCancel} variant="outlined">
              <FormattedMessage id="cancel" />
            </Button>
            <Button onClick={handleApply} variant="contained" disabled={!hasChanges} color="primary">
              <FormattedMessage id="apply" />
            </Button>
          </Box>
        </Box>
      </Popover>
    </div>
  );
};

export default SuggestionFilter;
