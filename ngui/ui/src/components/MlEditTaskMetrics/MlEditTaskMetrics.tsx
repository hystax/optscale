import { Stack } from "@mui/material";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { SPACING_2 } from "utils/layouts";
import MlTaskMetricsTable from "./MlTaskMetricsTable";

const MlEditTaskMetrics = ({ metrics, onAttachChange, isLoading = false, isUpdateLoading = false }) => (
  <Stack spacing={SPACING_2}>
    <div>
      <ContentBackdropLoader isLoading={isUpdateLoading}>
        <MlTaskMetricsTable metrics={metrics} isLoading={isLoading} onAttachChange={onAttachChange} />
      </ContentBackdropLoader>
    </div>
    <div>
      <InlineSeverityAlert messageId="mlTaskSpecificMetricsDescription" />
    </div>
  </Stack>
);

export default MlEditTaskMetrics;
