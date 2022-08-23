import React from "react";
import PropTypes from "prop-types";
import { getEnvironmentDisplayedName } from "utils/getEnvironmentDisplayName";

const LinkToEnvironmentDetails = ({ environment }) => {
  const displayedName = getEnvironmentDisplayedName(environment);

  const { id } = environment;

  return (
    <a href={`/resources/${id}`} target="_blank" rel="noopener noreferrer">
      {displayedName}
    </a>
  );
};

LinkToEnvironmentDetails.propTypes = {
  environment: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string,
    details: PropTypes.shape({
      cloud_resource_id: PropTypes.string.isRequired
    }).isRequired
  }).isRequired
};

export default LinkToEnvironmentDetails;
