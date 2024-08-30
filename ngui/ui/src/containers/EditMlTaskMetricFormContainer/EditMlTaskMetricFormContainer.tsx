import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MlTaskMetricForm from "components/forms/MlTaskMetricForm";
import { FIELD_NAMES } from "components/forms/MlTaskMetricForm/constants";
import MlTasksService from "services/MlTasksService";
import { ML_TASK_METRICS } from "urls";

const EditMlTaskMetricFormContainer = () => {
  const navigate = useNavigate();

  const { metricId } = useParams();

  const { useAlwaysGetGlobalMetric, useUpdateGlobalMetric } = MlTasksService();

  const { isLoading: isGetGlobalMetricLoading, metric } = useAlwaysGetGlobalMetric(metricId);

  const { onUpdate, isLoading: isUpdateGlobalMetricLoading } = useUpdateGlobalMetric(metricId);

  const redirect = () => navigate(ML_TASK_METRICS);

  const onSubmit = (formData) => {
    onUpdate(formData).then(() => {
      redirect();
    });
  };

  const onCancel = () => redirect();

  const defaultValues = useMemo(
    () => ({
      [FIELD_NAMES.NAME]: metric.name ?? "",
      [FIELD_NAMES.TENDENCY]: metric.tendency ?? "",
      [FIELD_NAMES.TARGET_VALUE]: metric.target_value ?? "",
      [FIELD_NAMES.FUNCTION]: metric.func ?? ""
    }),
    [metric.name, metric.func, metric.target_value, metric.tendency]
  );

  return (
    <MlTaskMetricForm
      defaultValues={defaultValues}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isGetLoading={isGetGlobalMetricLoading}
      isSubmitLoading={isUpdateGlobalMetricLoading}
      isEdit
    />
  );
};

export default EditMlTaskMetricFormContainer;
