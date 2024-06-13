import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import MlTaskMetricForm from "components/forms/MlTaskMetricForm";
import { FIELD_NAMES } from "components/forms/MlTaskMetricForm/constants";
import MlTasksService from "services/MlTasksService";
import { ML_TASK_METRICS } from "urls";

const CreateMlTaskMetricFormContainer = () => {
  const navigate = useNavigate();

  const { useCreateGlobalMetric } = MlTasksService();

  const { onCreate, isLoading } = useCreateGlobalMetric();

  const redirect = () => navigate(ML_TASK_METRICS);

  const onSubmit = (formData) => {
    onCreate(formData).then(() => {
      redirect();
    });
  };

  const onCancel = () => redirect();

  const defaultValues = useMemo(
    () => ({
      [FIELD_NAMES.NAME]: "",
      [FIELD_NAMES.KEY]: "",
      [FIELD_NAMES.TENDENCY]: "",
      [FIELD_NAMES.TARGET_VALUE]: 0,
      [FIELD_NAMES.FUNCTION]: ""
    }),
    []
  );

  return <MlTaskMetricForm defaultValues={defaultValues} onSubmit={onSubmit} onCancel={onCancel} isSubmitLoading={isLoading} />;
};

export default CreateMlTaskMetricFormContainer;
