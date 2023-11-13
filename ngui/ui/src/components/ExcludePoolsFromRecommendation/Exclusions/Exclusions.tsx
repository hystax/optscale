import Typography from "@mui/material/Typography";
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

export default Exclusions;
