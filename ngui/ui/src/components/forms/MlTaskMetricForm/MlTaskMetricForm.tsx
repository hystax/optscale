import { useEffect } from "react";
import { Box, Link } from "@mui/material";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PageContentWrapper from "components/PageContentWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ML_TASKS, ML_TASK_METRICS } from "urls";
import { SPACING_1 } from "utils/layouts";
import { NameField, KeyField, TendencySelector, AggregateFunctionSelector, TargetValueField } from "./FormElements";

const MlTaskMetricForm = ({
  onSubmit,
  isGetLoading = false,
  defaultValues,
  onCancel,
  isSubmitLoading = false,
  isEdit = false
}) => {
  const { isDemo } = useOrganizationInfo();

  const methods = useForm({ defaultValues });
  const { reset, handleSubmit } = methods;

  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  return (
    <>
      <ActionBar
        data={{
          breadcrumbs: [
            <Link key={1} to={ML_TASKS} component={RouterLink}>
              <FormattedMessage id="tasks" />
            </Link>,
            <Link key={2} to={ML_TASK_METRICS} component={RouterLink}>
              <FormattedMessage id="mlMetricsLibraryTitle" />
            </Link>,
            isEdit ? <span key={3}>{defaultValues.name}</span> : null
          ],
          title: {
            isLoading: isEdit && isGetLoading,
            messageId: isEdit ? "editMetricTitle" : "addMetricTitle",
            dataTestId: "lbl_add_metric"
          }
        }}
      />
      <PageContentWrapper>
        <Box sx={{ width: { md: "50%" }, mb: SPACING_1 }}>
          <FormProvider {...methods}>
            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              <NameField isLoading={isGetLoading} />
              {!isEdit && <KeyField isLoading={isGetLoading} />}
              <TendencySelector isLoading={isGetLoading} />
              <TargetValueField isLoading={isGetLoading} />
              <AggregateFunctionSelector isLoading={isGetLoading} />
              <FormButtonsWrapper>
                <SubmitButtonLoader
                  messageId={isEdit ? "save" : "create"}
                  isLoading={isSubmitLoading}
                  dataTestId="btn_create"
                  tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
                  disabled={isDemo}
                />
                <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
              </FormButtonsWrapper>
            </form>
          </FormProvider>
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default MlTaskMetricForm;
