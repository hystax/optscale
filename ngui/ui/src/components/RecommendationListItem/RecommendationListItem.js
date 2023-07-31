import React, { Fragment } from "react";
import PropTypes from "prop-types";

const RecommendationListItem = ({ elements }) => (
  <div style={{ display: "flex", alignItems: "center" }}>
    {elements.map(({ key, node }, i) => (
      <Fragment key={key}>
        {node}
        {i !== elements.length - 1 ? <>&nbsp;|&nbsp;</> : null}
      </Fragment>
    ))}
  </div>
);

RecommendationListItem.propTypes = {
  elements: PropTypes.arrayOf(PropTypes.node).isRequired
};

export default RecommendationListItem;
