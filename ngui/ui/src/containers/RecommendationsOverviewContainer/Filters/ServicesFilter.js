import React from "react";
import { FormControl, InputLabel, MenuItem, OutlinedInput, Select } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import CloudLabel from "components/CloudLabel";
import { ALL_SERVICES, useRecommendationServices } from "hooks/useRecommendationServices";

export const serviceFilter = (service) => (recommendation) => {
  if (service === ALL_SERVICES) {
    return true;
  }

  return recommendation.services.includes(service);
};

const renderItem = (type, name, intl) =>
  type ? <CloudLabel name={intl.formatMessage({ id: name })} type={type} disableLink /> : <FormattedMessage id={name} />;

const ServicesFilter = ({ onChange, value }) => {
  const intl = useIntl();
  const label = intl.formatMessage({ id: "applicableServices" });

  const services = useRecommendationServices();

  return (
    <FormControl sx={{ minWidth: "250px" }}>
      <InputLabel id="services-label">{label}</InputLabel>
      <Select
        labelId="services-label"
        id="services"
        value={value}
        onChange={({ target: { value: newValue } }) => onChange(newValue)}
        input={<OutlinedInput label={label} />}
        renderValue={(selected) => {
          const { name, type } = services[selected];
          return renderItem(type, name, intl);
        }}
      >
        {Object.entries(services).map(([key, { name, type }]) => (
          <MenuItem key={key} value={key}>
            {renderItem(type, name, intl)}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

ServicesFilter.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired
};

export default ServicesFilter;
