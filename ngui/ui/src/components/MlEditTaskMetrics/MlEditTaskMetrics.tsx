import ContentBackdropLoader from "components/ContentBackdropLoader";
import PageContentDescription from "components/PageContentDescription/PageContentDescription";
import MlTaskMetricsTable from "./MlTaskMetricsTable";

const MlEditTaskMetrics = ({ metrics, onAttachChange, isLoading = false, isUpdateLoading = false }) => (
  <>
    <ContentBackdropLoader isLoading={isUpdateLoading}>
      <MlTaskMetricsTable metrics={metrics} isLoading={isLoading} onAttachChange={onAttachChange} />
    </ContentBackdropLoader>
    <PageContentDescription
      position="bottom"
      alertProps={{
        messageId: "mlTaskSpecificMetricsDescription",
      }}
    />
  </>
);

export default MlEditTaskMetrics;
