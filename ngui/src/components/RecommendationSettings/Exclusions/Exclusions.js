import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ExcludedPoolsTable from "../ExcludedPoolsTable";

const Exclusions = ({
  availablePools,
  currentExcludedPools,
  setSelectedPools,
  isLoading,
  isChangeSettingsAllowed,
  onSelectionChange
}) => (
  <>
    <Typography gutterBottom>
      <FormattedMessage id="exclusionsDescription" values={{ strong: (chunks) => <strong>{chunks}</strong> }} />
    </Typography>
    <ExcludedPoolsTable
      availablePools={availablePools}
      currentExcludedPools={currentExcludedPools}
      setSelectedPools={setSelectedPools}
      isLoading={isLoading}
      isChangeSettingsAllowed={isChangeSettingsAllowed}
      onSelectionChange={onSelectionChange}
    />
  </>
);

Exclusions.propTypes = {
  availablePools: PropTypes.array,
  currentExcludedPools: PropTypes.object,
  setSelectedPools: PropTypes.func,
  isLoading: PropTypes.bool,
  isChangeSettingsAllowed: PropTypes.bool,
  onSelectionChange: PropTypes.func
};

export default Exclusions;
