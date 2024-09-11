import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import MlMetricForm from "components/forms/MlMetricForm";
import { FIELD_NAMES } from "components/forms/MlMetricForm/constants";
import MlMetricsService from "services/MlMetricsService";
import { ML_METRICS } from "urls";

const CreateMlMetricFormContainer = () => {
  const navigate = useNavigate();

  const { useCreateMlMetric } = MlMetricsService();

  const { onCreate, isLoading } = useCreateMlMetric();

  const redirect = () => navigate(ML_METRICS);

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

  return <MlMetricForm defaultValues={defaultValues} onSubmit={onSubmit} onCancel={onCancel} isSubmitLoading={isLoading} />;
};

export default CreateMlMetricFormContainer;
