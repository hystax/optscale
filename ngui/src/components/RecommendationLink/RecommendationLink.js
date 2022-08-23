import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";
import { COST_CATEGORY, SECURITY_CATEGORY } from "components/RelevantRecommendations/constants";
import { getRecommendationsUrl } from "urls";

const RecommendationLink = ({ category, children, dataTestId }) => (
  <Link to={getRecommendationsUrl({ category })} component={RouterLink} data-test-id={dataTestId}>
    {children}
  </Link>
);

RecommendationLink.propTypes = {
  children: PropTypes.node.isRequired,
  category: PropTypes.oneOf([COST_CATEGORY, SECURITY_CATEGORY]),
  dataTestId: PropTypes.string
};

export default RecommendationLink;
