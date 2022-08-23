import React from "react";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import Icon from "components/Icon";

const RecommendationLimitWarning = ({ limit }) => {
  const intl = useIntl();

  return (
    <div style={{ display: "flex" }}>
      <Icon icon={InfoOutlinedIcon} hasRightMargin color="warning" />
      <Typography>
        <FormattedMessage
          id="rowsLimitWarning"
          values={{
            entities: intl.formatMessage({ id: "recommendations" }).toLocaleLowerCase(),
            count: limit
          }}
        />
      </Typography>
    </div>
  );
};

RecommendationLimitWarning.propTypes = {
  limit: PropTypes.number.isRequired
};

export default RecommendationLimitWarning;
