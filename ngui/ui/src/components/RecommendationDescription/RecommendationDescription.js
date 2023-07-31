import React from "react";
import { Typography } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";

const RecommendationDescription = ({ messageId, messageValues = {}, dataTestId, isLoading = false }) =>
  isLoading ? (
    <Skeleton />
  ) : (
    <Typography data-test-id={dataTestId}>
      <FormattedMessage id={messageId} values={messageValues} />
    </Typography>
  );

RecommendationDescription.propTypes = {
  messageId: PropTypes.string.isRequired,
  messageValues: PropTypes.object,
  dataTestId: PropTypes.string,
  isLoading: PropTypes.bool
};

export default RecommendationDescription;
