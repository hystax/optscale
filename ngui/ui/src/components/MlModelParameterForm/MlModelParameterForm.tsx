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
import { ML_MODELS, ML_MODELS_PARAMETERS } from "urls";
import { SPACING_1 } from "utils/layouts";
import { NameField, KeyField, TendencySelector, DefaultGoalValueField, AggregateFunctionSelector } from "./FormElements";

export const ML_MODEL_PARAMETER_FORM_FIELD_NAMES = Object.freeze({
  NAME: "name",
  KEY: "key",
  TENDENCY: "tendency",
  TARGET_VALUE: "target_value",
  FUNCTION: "function"
});

const MlModelParameterForm = ({
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
            <Link key={1} to={ML_MODELS} component={RouterLink}>
              <FormattedMessage id="models" />
            </Link>,
            <Link key={2} to={ML_MODELS_PARAMETERS} component={RouterLink}>
              <FormattedMessage id="mlParametersLibraryTitle" />
            </Link>,
            isEdit ? <span key={3}>{defaultValues.name}</span> : null
          ],
          title: {
            isLoading: isEdit && isGetLoading,
            messageId: isEdit ? "editParameterTitle" : "addParameterTitle",
            dataTestId: "lbl_add_parameter"
          }
        }}
      />
      <PageContentWrapper>
        <Box sx={{ width: { md: "50%" }, mb: SPACING_1 }}>
          <FormProvider {...methods}>
            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              <NameField name={ML_MODEL_PARAMETER_FORM_FIELD_NAMES.NAME} isLoading={isGetLoading} />
              {!isEdit && <KeyField name={ML_MODEL_PARAMETER_FORM_FIELD_NAMES.KEY} isLoading={isGetLoading} />}
              <TendencySelector name={ML_MODEL_PARAMETER_FORM_FIELD_NAMES.TENDENCY} isLoading={isGetLoading} />
              <DefaultGoalValueField name={ML_MODEL_PARAMETER_FORM_FIELD_NAMES.TARGET_VALUE} isLoading={isGetLoading} />
              <AggregateFunctionSelector name={ML_MODEL_PARAMETER_FORM_FIELD_NAMES.FUNCTION} isLoading={isGetLoading} />
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

export default MlModelParameterForm;
