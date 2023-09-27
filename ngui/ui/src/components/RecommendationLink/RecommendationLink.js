import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";
import {
  CATEGORY_COST,
  CATEGORY_CRITICAL,
  CATEGORY_SECURITY
} from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import { getRecommendationsUrl } from "urls";

const RecommendationLink = ({ category, children, dataTestId }) => (
  <Link to={getRecommendationsUrl({ category })} component={RouterLink} data-test-id={dataTestId}>
    {children}
  </Link>
);

RecommendationLink.propTypes = {
  children: PropTypes.node.isRequired,
  category: PropTypes.oneOf([CATEGORY_COST, CATEGORY_SECURITY, CATEGORY_CRITICAL]),
  dataTestId: PropTypes.string
};

export default RecommendationLink;
