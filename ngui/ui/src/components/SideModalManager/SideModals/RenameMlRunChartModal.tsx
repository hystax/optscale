import React from "react";
import { FormProvider, useForm, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import BaseSideModal from "./BaseSideModal";

const FIELD_NAME = "name";

const NameField = () => {
  const intl = useIntl();
  const {
    register,
    formState: { errors }
  } = useFormContext();

  return (
    <Input
      required
      autoFocus
      dataTestId="input_chart_name"
      error={!!errors[FIELD_NAME]}
      helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
      label={<FormattedMessage id="name" />}
      {...register(FIELD_NAME, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: DEFAULT_MAX_INPUT_LENGTH,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "name" }), max: DEFAULT_MAX_INPUT_LENGTH }
          )
        }
      })}
    />
  );
};

const Form = ({ chartName, onRename, closeSideModal }) => {
  const methods = useForm({
    defaultValues: {
      name: chartName
    }
  });

  const { handleSubmit } = methods;

  const onSubmit = (formData) => {
    onRename(formData[FIELD_NAME]);
    closeSideModal();
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <NameField />
        <FormButtonsWrapper>
          <ButtonLoader
            dataTestId="btn_rename_ml_run_chart"
            loaderDataTestId="loading_btn_rename_ml_run_chart"
            messageId="save"
            color="primary"
            variant="contained"
            type="submit"
          />
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

class RenameMlRunChartModal extends BaseSideModal {
  headerProps = {
    messageId: "renameMlChartTitle",
    color: "primary",
    dataTestIds: {
      title: "lbl_rename_ml_run_chart",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_rename_ml_run_chart";

  get content() {
    return <Form closeSideModal={this.closeSideModal} chartName={this.payload?.chartName} onRename={this.payload?.onRename} />;
  }
}

export default RenameMlRunChartModal;
