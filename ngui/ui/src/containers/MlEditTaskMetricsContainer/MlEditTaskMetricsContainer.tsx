import { useParams } from "react-router-dom";
import MlEditTaskMetrics from "components/MlEditTaskMetrics";
import MlMetricsService from "services/MlMetricsService";
import MlTasksService from "services/MlTasksService";

const MlEditTaskMetricsContainer = ({ taskMetrics }) => {
  const getMetrics = (globalMetrics) => {
    const metrics = globalMetrics.map((globalMetric) => {
      const isAttached = !!taskMetrics.find((taskMetric) => taskMetric.key === globalMetric.key);

      return {
        is_attached: isAttached,
        ...globalMetric
      };
    });

    return metrics;
  };

  const { taskId } = useParams();

  const { useUpdateTask } = MlTasksService();
  const { useGetMlMetrics } = MlMetricsService();

  const { isLoading: isGetMlMetricsLoading, metrics: globalMetrics } = useGetMlMetrics();
  const { onUpdate, isLoading: isUpdateLoading } = useUpdateTask();

  const onAttachChange = (formData) => {
    onUpdate(taskId, formData);
  };

  return (
    <MlEditTaskMetrics
      metrics={getMetrics(globalMetrics)}
      onAttachChange={onAttachChange}
      isLoading={isGetMlMetricsLoading}
      isUpdateLoading={isUpdateLoading}
    />
  );
};

export default MlEditTaskMetricsContainer;
