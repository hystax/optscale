import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ExcludedPoolsTable from "./ExcludedPoolsTable";

const Exclusions = ({
  availablePools,
  currentExcludedPools,
  isLoading,
  isChangeSettingsAllowed,
  selectedPoolIds,
  onSelectedPoolIdsChange
}) => (
  <>
    <Typography gutterBottom>
      <FormattedMessage id="exclusionsDescription" values={{ strong: (chunks) => <strong>{chunks}</strong> }} />
    </Typography>
    <ExcludedPoolsTable
      availablePools={availablePools}
      currentExcludedPools={currentExcludedPools}
      isLoading={isLoading}
      isChangeSettingsAllowed={isChangeSettingsAllowed}
      selectedPoolIds={selectedPoolIds}
      onSelectedPoolIdsChange={onSelectedPoolIdsChange}
    />
  </>
);

Exclusions.propTypes = {
  availablePools: PropTypes.array,
  currentExcludedPools: PropTypes.object,
  isLoading: PropTypes.bool,
  isChangeSettingsAllowed: PropTypes.bool,
  selectedPoolIds: PropTypes.array,
  onSelectedPoolIdsChange: PropTypes.func
};

export default Exclusions;
