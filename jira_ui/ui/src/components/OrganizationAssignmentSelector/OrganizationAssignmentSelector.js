import React from "react";
import Select from "@atlaskit/select";
import PropTypes from "prop-types";

const OrganizationAssignmentSelector = ({ options, defaultValue, onChange, isLoading }) => (
  <>
    <label htmlFor="organization-select" style={{ display: "inline-block", marginBottom: "16px" }}>
      Select OptScale organization that will be used for this Jira instance
    </label>
    <Select
      defaultValue={defaultValue}
      isLoading={isLoading}
      isDisabled={isLoading}
      getOptionValue={(option) => option.id}
      getOptionLabel={(option) => option.name}
      onChange={onChange}
      inputId="organization-select"
      options={options}
      placeholder="Organization"
    />
  </>
);

OrganizationAssignmentSelector.propTypes = {
  options: PropTypes.array.isRequired,
  onChange: PropTypes.func.isRequired,
  value: PropTypes.shape({
    value: PropTypes.string,
    label: PropTypes.string
  }),
  isLoading: PropTypes.bool,
  defaultValue: PropTypes.string
};

export default OrganizationAssignmentSelector;
