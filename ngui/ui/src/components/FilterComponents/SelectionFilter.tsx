import React, { useId, useMemo, useState } from "react";
import SearchIcon from "@mui/icons-material/Search";
import {
  Box,
  Checkbox,
  FormControlLabel,
  FormGroup,
  InputAdornment,
  Popover,
  TextField,
  Typography,
  Divider,
} from "@mui/material";
import Button from "@mui/material/Button";
import { FormattedMessage, useIntl } from "react-intl";
import { useDebouncedValue } from "hooks/useDebouncedValue";
import { isEmptyArray } from "utils/arrays";

type SelectionStateButtonProps = {
  appliedItems: string[];
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
  id: string;
  label: React.ReactNode;
  icon?: React.ReactNode;
  selectionLabel: () => React.ReactNode;
};

type Value = string;

type FilterItem = {
  value: Value;
  [key: string]: unknown;
};

type FilterSettings = {
  [key: string]: boolean;
};

type AppliedFilter = {
  values: Value[];
  settings?: FilterSettings;
};

type FiltersProps<T extends FilterItem> = {
  items: T[];
  label: React.ReactNode;
  buttonIcon?: React.ReactNode;
  renderItem: (item: T) => React.ReactNode;
  renderSelectedItem: (item: T) => React.ReactNode;
  searchPredicate: (item: T, searchQuery: string) => boolean;
  searchPlaceholder?: string;
  onChange?: (selectedItems: AppliedFilter) => void;
  appliedItems: AppliedFilter;
  settings?: {
    name: string;
    label: React.ReactNode;
  }[];
};

const SelectionStateButton = ({ appliedItems, onClick, id, label, icon, selectionLabel }: SelectionStateButtonProps) => (
  <Button
    aria-describedby={id}
    variant={appliedItems.length > 0 ? "contained" : "outlined"}
    onClick={onClick}
    color="primary"
    startIcon={icon}
  >
    {label} ({selectionLabel()})
  </Button>
);

const SelectionFilter = <T extends FilterItem>({
  items,
  label,
  buttonIcon,
  renderItem,
  renderSelectedItem,
  searchPredicate,
  onChange,
  appliedItems,
  settings = [],
}: FiltersProps<T>) => {
  const intl = useIntl();

  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const [selectedValues, setSelectedValues] = useState<Value[]>([]);
  const [selectedSettings, setSelectedSettings] = useState<FilterSettings>({});

  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebouncedValue(searchQuery, { delay: 300 });

  // Create a map of available values for quick lookup
  const valueItemsMap = useMemo(() => new Map(items.map((item) => [item.value, item])), [items]);

  // Combine available and unavailable items
  const allItems = useMemo(() => {
    const unavailableItems = appliedItems.values
      .filter((value) => !valueItemsMap.has(value))
      .map((value) => ({ value, name: value }));
    return [...items, ...unavailableItems];
  }, [items, appliedItems.values, valueItemsMap]);

  const popoverId = useId();

  const onOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
    setSelectedValues(appliedItems.values);
    setSelectedSettings(appliedItems.settings || {});
    setSearchQuery("");
  };

  const handleCancel = () => {
    setAnchorEl(null);
    setSelectedValues(appliedItems.values);
    setSelectedSettings(appliedItems.settings || {});
    setSearchQuery("");
  };

  const handleApply = () => {
    setAnchorEl(null);
    setSearchQuery("");

    onChange?.({
      values: selectedValues,
      settings: selectedSettings,
    });
  };

  const handleSettingChange = (name: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedSettings((prev) => ({
      ...prev,
      [name]: event.target.checked,
    }));
  };

  const handleItemToggle = (newValue: Value) => {
    setSelectedValues((prev) => {
      if (prev.includes(newValue)) {
        return prev.filter((value) => value !== newValue);
      } else {
        return [...prev, newValue];
      }
    });
  };

  const open = Boolean(anchorEl);
  const id = open ? `filter-popover-${popoverId}` : `filter-popover-${popoverId}-closed`;

  const hasChanges =
    JSON.stringify(selectedValues) !== JSON.stringify(appliedItems.values) ||
    JSON.stringify(selectedSettings) !== JSON.stringify(appliedItems.settings || {});

  const filteredItems = allItems
    .filter((item) => {
      const isUnavailable = !valueItemsMap.has(item.value);

      if (isUnavailable) {
        return item.value.toString().toLocaleLowerCase().includes(debouncedSearchQuery.toLocaleLowerCase());
      }
      return searchPredicate(item as T, debouncedSearchQuery);
    })
    .sort((a, b) => {
      const isAUnavailable = !valueItemsMap.has(a.value);
      const isBUnavailable = !valueItemsMap.has(b.value);
      // Sort unavailable items to the top
      if (isAUnavailable && !isBUnavailable) {
        return -1;
      }
      if (!isAUnavailable && isBUnavailable) {
        return 1;
      }
      return 0;
    });

  const filteredValues = filteredItems.map((item) => item.value);

  const allFilteredSelected = filteredValues.length > 0 && filteredValues.every((value) => selectedValues.includes(value));

  const someFilteredSelected =
    filteredValues.length > 0 && filteredValues.some((value) => selectedValues.includes(value)) && !allFilteredSelected;

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      setSelectedValues(filteredValues);
    } else {
      setSelectedValues([]);
    }
  };

  const getSelectAllLabel = () => {
    if (debouncedSearchQuery) {
      return <FormattedMessage id="filteredResults" values={{ count: filteredItems.length }} />;
    }
    if (isEmptyArray(selectedValues)) {
      return <FormattedMessage id="selectAll" />;
    }
    return <FormattedMessage id="countOfTotalSelected" values={{ count: selectedValues.length, total: allItems.length }} />;
  };

  const renderFilterContent = () => {
    if (isEmptyArray(allItems)) {
      return (
        <Typography variant="body2" textAlign="center" sx={{ py: 2, px: 1, wordBreak: "break-all" }}>
          <FormattedMessage id="noFiltersAvailable" />
        </Typography>
      );
    }

    return (
      <>
        {isEmptyArray(settings) ? null : (
          <>
            <Typography variant="subtitle2" color="primary" sx={{ pt: 2, px: 2, fontWeight: "bold" }}>
              <FormattedMessage id="settings" />
            </Typography>
            <Box sx={{ px: 2, pb: 0 }}>
              {settings.map((setting) => (
                <FormControlLabel
                  key={setting.name}
                  control={
                    <Checkbox checked={selectedSettings[setting.name] || false} onChange={handleSettingChange(setting.name)} />
                  }
                  label={setting.label}
                />
              ))}
            </Box>
            <Divider />
            <Typography variant="subtitle2" color="primary" sx={{ pt: 2, px: 2, fontWeight: "bold" }}>
              <FormattedMessage id="filters" />
            </Typography>
          </>
        )}
        <Box sx={{ px: 2, borderBottom: 1, borderColor: "divider", pb: 1, pt: 1 }}>
          <TextField
            size="small"
            placeholder={intl.formatMessage({ id: "search" })}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            fullWidth
            variant="standard"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
          />
        </Box>
        <FormGroup>
          {filteredItems.length > 1 && (
            <>
              <FormControlLabel
                control={
                  <Checkbox checked={allFilteredSelected} indeterminate={someFilteredSelected} onChange={handleSelectAll} />
                }
                label={getSelectAllLabel()}
                sx={{ px: 2, py: 0 }}
              />
              <Divider />
            </>
          )}
          {filteredItems.length > 0 && (
            <Box sx={{ maxHeight: "300px", overflowY: "auto", overflowX: "hidden" }}>
              <Box sx={{ py: 0.5 }}>
                {filteredItems.map((item) => (
                  <FormControlLabel
                    key={item.value}
                    control={
                      <Checkbox
                        checked={selectedValues.some((i) => i === item.value)}
                        onChange={() => handleItemToggle(item.value)}
                      />
                    }
                    label={valueItemsMap.has(item.value) ? renderItem(item as T) : String(item.value)}
                    sx={{
                      px: 2,
                      width: "100%",
                      overflowWrap: "anywhere",
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}
          {filteredItems.length === 0 && (
            <Typography variant="body2" textAlign="center" sx={{ py: 1, px: 1, overflowWrap: "anywhere" }}>
              <FormattedMessage id="noMatches" values={{ searchQuery: debouncedSearchQuery }} />
            </Typography>
          )}
        </FormGroup>
      </>
    );
  };

  return (
    <>
      <SelectionStateButton
        appliedItems={appliedItems.values}
        onClick={onOpen}
        id={id}
        label={label}
        selectionLabel={() => {
          if (isEmptyArray(appliedItems.values)) {
            return <FormattedMessage id="any" />;
          }

          const firstValue = appliedItems.values[0];
          const renderedFirstItem = valueItemsMap.has(firstValue)
            ? renderSelectedItem(valueItemsMap.get(firstValue) as T)
            : String(firstValue);

          if (appliedItems.values.length === 1) {
            return renderedFirstItem;
          }

          return (
            <>
              {renderedFirstItem}, +{appliedItems.values.length - 1}
            </>
          );
        }}
        icon={buttonIcon}
      />
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
        <Box sx={{ display: "flex", flexDirection: "column", width: "300px" }}>
          {renderFilterContent()}
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
    </>
  );
};

export default SelectionFilter;
