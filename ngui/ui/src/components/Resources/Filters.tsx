import { useState } from "react";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import RestartAltOutlinedIcon from "@mui/icons-material/RestartAltOutlined";
import { Badge, Box } from "@mui/material";
import Button from "@mui/material/Button";
import { FormattedMessage, useIntl } from "react-intl";
import { RangeFilter, SelectionFilter, SuggestionFilter } from "components/FilterComponents";
import { FILTER_CONFIGS } from "components/Resources/filterConfigs";
import { useCurrentEmployee } from "hooks/coreData/useCurrentEmployee";
import { endOfDay, moveDateFromUTC, startOfDay } from "utils/datetime";

const getSelectionFilterProps = ({ config, onChange, appliedFilters, data }) => ({
  items: config.transformers.getItems(data),
  label: config.label,
  buttonIcon: config.icon,
  renderItem: config.renderItem,
  renderSelectedItem: config.renderSelectedItem,
  searchPredicate: config.searchPredicate,
  onChange: onChange(config.id),
  appliedItems: appliedFilters[config.id],
  settings: config.settings,
});

const getRangeFilterProps = ({ config, onChange, appliedFilters }) => ({
  label: config.label,
  onChange: onChange(config.id),
  appliedRange: config.transformers.getAppliedRange(appliedFilters[config.id]),
});

const ResourceFilters = ({ filters, appliedFilters, onAppliedFiltersChange }) => {
  const intl = useIntl();

  const handleChange = (type) => (selectedItems) => {
    onAppliedFiltersChange({
      [type]: selectedItems,
    });
  };

  const handleRangeChange = (type) => (selectedRange) => {
    onAppliedFiltersChange({
      [type]: {
        from: selectedRange.from ? moveDateFromUTC(startOfDay(selectedRange.from)) : undefined,
        to: selectedRange.to ? moveDateFromUTC(endOfDay(selectedRange.to)) : undefined,
      },
    });
  };

  const [showMoreFilters, setShowMoreFilters] = useState(false);

  const toggleShowMoreFilters = () => {
    setShowMoreFilters((prev) => !prev);
  };

  const handleResetFilters = () => {
    onAppliedFiltersChange(
      Object.fromEntries(Object.values(FILTER_CONFIGS).map((config) => [config.id, config.getDefaultValue()]))
    );
  };

  const { id: currentEmployeeId } = useCurrentEmployee();

  const suggestionGroups = [
    {
      id: "ownerId",
      title: <FormattedMessage id="owner" />,
      items:
        filters.owner
          ?.filter((item) => item.id === currentEmployeeId)
          .map((item) => ({
            name: intl.formatMessage({ id: "assignedToMe" }),
            value: item.id,
          })) ?? [],
      renderItem: (item) => item.name,
    },
    {
      id: "resourceType",
      title: <FormattedMessage id="resourceType" />,
      items:
        filters.resource_type
          ?.filter((item) => ["Volume", "Instance"].includes(item.name))
          .map((item) => ({
            name: item.name,
            value: `${item.name}:${item.type}`,
          })) ?? [],
      renderItem: (item) => item.name,
    },
    {
      id: "active",
      title: <FormattedMessage id="activity" />,
      items:
        filters.active
          ?.filter((item) => item === true)
          .map((item) => ({
            name: intl.formatMessage({ id: "active" }),
            value: item,
          })) ?? [],
      renderItem: (item) => item.name,
    },
    {
      id: "constraintViolated",
      title: <FormattedMessage id="constraintViolations" />,
      items:
        filters.constraint_violated
          ?.filter((item) => item === true)
          .map((item) => ({
            name: intl.formatMessage({ id: "violated" }),
            value: item,
          })) ?? [],
      renderItem: (item) => item.name,
    },
  ];

  const handleApplySuggestion = (updates: Record<string, string[]>) => {
    onAppliedFiltersChange({
      ownerId: { values: updates.ownerId || [] },
      resourceType: { values: updates.resourceType || [] },
      active: { values: updates.active || [] },
      constraintViolated: { values: updates.constraintViolated || [] },
    });
  };

  const FILTER_GROUPS = {
    primary: [
      { key: "cloudAccountId", data: filters.cloud_account },
      { key: "poolId", data: filters.pool },
      { key: "ownerId", data: filters.owner },
      { key: "region", data: filters.region },
      { key: "serviceName", data: filters.service_name },
      { key: "resourceType", data: filters.resource_type },
      { key: "active", data: filters.active },
      { key: "recommendations", data: filters.recommendations },
      { key: "constraintViolated", data: filters.constraint_violated },
    ],
    range: [{ key: "firstSeen" }, { key: "lastSeen" }],
    secondary: [
      { key: "tag", data: filters.tag },
      { key: "withoutTag", data: filters.without_tag },
      { key: "meta", data: filters.meta },
      { key: "networkTrafficFrom", data: filters.traffic_from },
      { key: "networkTrafficTo", data: filters.traffic_to },
      { key: "k8sNode", data: filters.k8s_node },
      { key: "k8sService", data: filters.k8s_service },
      { key: "k8sNamespace", data: filters.k8s_namespace },
    ],
  };

  const hasAppliedValue = (key) => {
    const config = FILTER_CONFIGS[key];
    return config.isApplied(appliedFilters[key]);
  };

  const appliedSecondaryFilters = FILTER_GROUPS.secondary.filter(({ key }) => hasAppliedValue(key));

  return (
    <Box display="flex" gap={2} flexWrap="wrap">
      <SuggestionFilter
        suggestionGroups={suggestionGroups}
        label={<FormattedMessage id="suggestions" />}
        onApplySuggestion={handleApplySuggestion}
        appliedFilters={{
          ownerId: appliedFilters.ownerId.values,
          resourceType: appliedFilters.resourceType.values,
          active: appliedFilters.active.values,
          constraintViolated: appliedFilters.constraintViolated.values,
        }}
      />
      {FILTER_GROUPS.primary.map(({ key, data }) => (
        <SelectionFilter
          key={key}
          {...getSelectionFilterProps({ config: FILTER_CONFIGS[key], onChange: handleChange, appliedFilters, data })}
        />
      ))}
      {FILTER_GROUPS.range.map(({ key }) => (
        <RangeFilter
          key={key}
          {...getRangeFilterProps({ config: FILTER_CONFIGS[key], onChange: handleRangeChange, appliedFilters })}
        />
      ))}
      {showMoreFilters ? (
        FILTER_GROUPS.secondary.map(({ key, data }) => (
          <SelectionFilter
            key={key}
            {...getSelectionFilterProps({ config: FILTER_CONFIGS[key], onChange: handleChange, appliedFilters, data })}
          />
        ))
      ) : (
        <>
          {appliedSecondaryFilters.map(({ key, data }) => (
            <SelectionFilter
              key={key}
              {...getSelectionFilterProps({ config: FILTER_CONFIGS[key], onChange: handleChange, appliedFilters, data })}
            />
          ))}
        </>
      )}
      {
        // Do not show the button if all secondary filters are applied
        appliedSecondaryFilters.length === FILTER_GROUPS.secondary.length ? null : (
          <Badge
            badgeContent={showMoreFilters ? null : FILTER_GROUPS.secondary.length - appliedSecondaryFilters.length}
            color="primary"
          >
            <Button
              variant="text"
              color="primary"
              endIcon={showMoreFilters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              onClick={toggleShowMoreFilters}
            >
              <FormattedMessage id={showMoreFilters ? "showLess" : "showMore"} />
            </Button>
          </Badge>
        )
      }
      {/* Reset filters button */}
      {Object.keys(appliedFilters).some((key) => hasAppliedValue(key)) && (
        <Button variant="text" color="primary" startIcon={<RestartAltOutlinedIcon />} onClick={handleResetFilters}>
          <FormattedMessage id="resetFilters" />
        </Button>
      )}
    </Box>
  );
};

export default ResourceFilters;
