import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";
import {
  CATEGORY_COST,
  CATEGORY_CRITICAL,
  CATEGORY_SECURITY
} from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import {
  ALIBABA_EBS,
  ALIBABA_ECS,
  ALIBABA_ECS_VPC,
  ALL_SERVICES,
  ALIBABA_RDS,
  AWS_IAM,
  AWS_EC2,
  AWS_EC2_EBS,
  AWS_EC2_VPC,
  AWS_RDS,
  AWS_KINESIS,
  AWS_S3,
  AZURE_COMPUTE,
  AZURE_NETWORK,
  GCP_COMPUTE_ENGINE,
  NEBIUS_SERVICE
} from "hooks/useRecommendationServices";
import { getRecommendationsUrl } from "urls";

const RecommendationLink = ({ category, service, children, dataTestId }) => (
  <Link to={getRecommendationsUrl({ category, service })} component={RouterLink} data-test-id={dataTestId}>
    {children}
  </Link>
);

RecommendationLink.propTypes = {
  children: PropTypes.node.isRequired,
  category: PropTypes.oneOf([CATEGORY_COST, CATEGORY_SECURITY, CATEGORY_CRITICAL]),
  service: PropTypes.oneOf([
    ALL_SERVICES,
    ALIBABA_ECS,
    ALIBABA_ECS_VPC,
    ALIBABA_EBS,
    ALIBABA_RDS,
    AWS_IAM,
    AWS_EC2,
    AWS_EC2_EBS,
    AWS_EC2_VPC,
    AWS_RDS,
    AWS_KINESIS,
    AWS_S3,
    AZURE_COMPUTE,
    AZURE_NETWORK,
    GCP_COMPUTE_ENGINE,
    NEBIUS_SERVICE
  ]),
  dataTestId: PropTypes.string
};

export default RecommendationLink;
