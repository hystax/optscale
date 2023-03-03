import React, { useEffect } from "react";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PageContentWrapper from "components/PageContentWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { SPACING_1 } from "utils/layouts";
import { NameField, KeyField, TendencySelector, DefaultGoalValue, AggregateFunctionSelector } from "./FormElements";

export const ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES = Object.freeze({
  NAME: "name",
  KEY: "key",
  TENDENCY: "tendency",
  TARGET_VALUE: "target_value",
  FUNCTION: "function"
});

const MlApplicationParameterForm = ({
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
          title: {
            isLoading: isEdit && isGetLoading,
            text: isEdit ? (
              <FormattedMessage id="editGlobalParameterParameter" values={{ parameterName: defaultValues.name }} />
            ) : (
              <FormattedMessage id="addParameterTitle" />
            ),
            dataTestId: "lbl_add_parameter"
          }
        }}
      />
      <PageContentWrapper>
        <Box sx={{ width: { md: "50%" }, mb: SPACING_1 }}>
          <FormProvider {...methods}>
            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              <NameField name={ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.NAME} isLoading={isGetLoading} />
              {!isEdit && <KeyField name={ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.KEY} isLoading={isGetLoading} />}
              <TendencySelector name={ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.TENDENCY} isLoading={isGetLoading} />
              <DefaultGoalValue name={ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.TARGET_VALUE} isLoading={isGetLoading} />
              <AggregateFunctionSelector name={ML_APPLICATION_PARAMETER_FORM_FIELD_NAMES.FUNCTION} isLoading={isGetLoading} />
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

MlApplicationParameterForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  defaultValues: PropTypes.object.isRequired,
  isSubmitLoading: PropTypes.bool,
  isGetLoading: PropTypes.bool,
  isEdit: PropTypes.bool
};

export default MlApplicationParameterForm;
