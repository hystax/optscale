import React from "react";
import PropTypes from "prop-types";
import CircleLabel from "components/CircleLabel";
import CloudResourceId from "components/CloudResourceId";

const ResourceLabel = ({ resourceId, cloudResourceIdentifier, isActive, FigureLabelProps, separator, dataTestIds = {} }) => {
  const { label: labelDataTestId } = dataTestIds;

  const cloudResourceIdLabel = (
    <CloudResourceId
      resourceId={resourceId}
      cloudResourceIdentifier={cloudResourceIdentifier}
      separator={separator}
      dataTestId={labelDataTestId}
    />
  );

  return isActive ? (
    <CircleLabel
      figureColor="success"
      label={cloudResourceIdLabel}
      tooltip={{ show: true, messageId: "active" }}
      {...FigureLabelProps}
    />
  ) : (
    cloudResourceIdLabel
  );
};

ResourceLabel.propTypes = {
  cloudResourceIdentifier: PropTypes.string.isRequired,
  resourceId: PropTypes.string,
  isActive: PropTypes.bool,
  FigureLabelProps: PropTypes.object,
  separator: PropTypes.string,
  dataTestIds: PropTypes.shape({
    figure: PropTypes.string,
    label: PropTypes.string
  })
};

export default ResourceLabel;
