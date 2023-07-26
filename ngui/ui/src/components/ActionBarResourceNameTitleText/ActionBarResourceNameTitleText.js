import React from "react";
import PropTypes from "prop-types";
import Tooltip from "components/Tooltip";
import { useIsDownMediaQuery } from "hooks/useMediaQueries";
import { sliceFromEndByLimitWithEllipsis } from "utils/strings";

const RESOURCE_NAME_LENGTH_LIMIT = 20;

const ActionBarResourceNameTitleText = ({ resourceName = "", renderTitleLabel }) => {
  const shouldSliceTitle = useIsDownMediaQuery("lg");

  if (shouldSliceTitle) {
    const slicedResourceDisplayedName = sliceFromEndByLimitWithEllipsis(resourceName, RESOURCE_NAME_LENGTH_LIMIT);

    const titleLabel = typeof renderTitleLabel === "function" ? renderTitleLabel(resourceName) : resourceName;

    return (
      <Tooltip title={titleLabel} placement="right">
        <span>{slicedResourceDisplayedName}</span>
      </Tooltip>
    );
  }

  return typeof renderTitleLabel === "function" ? renderTitleLabel(resourceName) : resourceName;
};

ActionBarResourceNameTitleText.propTypes = {
  resourceName: PropTypes.string,
  renderTitleLabel: PropTypes.func
};

export default ActionBarResourceNameTitleText;
