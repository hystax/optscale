import { useEffect } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { isDefaultDashboard } from "hooks/useTaskRunChartState";
import { FIELD_NAMES, SAVE_AS_VALUES } from "./constants";
import { FormButtons, NameField, SaveAsRadioGroup, ShareSwitch } from "./FormElements";
import { FormValues } from "./types";
import { getDefaultValues } from "./utils";

const SaveMlChartsDashboardForm = ({
  dashboard,
  isOwnedDashboard,
  updateDashboard,
  createDashboard,
  onSuccess,
  onCancel,
  isLoadingProps = {}
}) => {
  const { isSubmitLoading } = isLoadingProps;

  const isDefault = isDefaultDashboard(dashboard.id);

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      name: dashboard.name,
      saveAs: !isOwnedDashboard || isDefault ? SAVE_AS_VALUES.SAVE_AS_NEW : SAVE_AS_VALUES.SAVE_THIS,
      share: dashboard.shared
    }),
    shouldUnregister: true
  });

  const { handleSubmit, watch, clearErrors, setFocus } = methods;

  const onSubmit = handleSubmit((formValues) => {
    const saveAsNew = formValues[FIELD_NAMES.SAVE_AS] === SAVE_AS_VALUES.SAVE_AS_NEW;

    if (saveAsNew) {
      return createDashboard({
        name: formValues[FIELD_NAMES.NAME],
        shared: formValues[FIELD_NAMES.SHARE]
      }).then(onSuccess);
    }

    return updateDashboard({
      name: dashboard.name,
      shared: formValues[FIELD_NAMES.SHARE]
    }).then(onSuccess);
  });

  const saveAs = watch(FIELD_NAMES.SAVE_AS);

  useEffect(() => {
    if (saveAs === SAVE_AS_VALUES.SAVE_AS_NEW) {
      setFocus(FIELD_NAMES.NAME);
    } else {
      clearErrors();
    }
  }, [saveAs, clearErrors, setFocus]);

  return (
    <FormProvider {...methods}>
      <form data-test-id="form_save_dashboard" onSubmit={onSubmit} noValidate>
        <SaveAsRadioGroup saveThisDisabled={!isOwnedDashboard || isDefault} />
        <NameField disabled={saveAs === SAVE_AS_VALUES.SAVE_THIS} />
        <ShareSwitch />
        <FormButtons onCancel={onCancel} isLoading={isSubmitLoading} />
      </form>
    </FormProvider>
  );
};

export default SaveMlChartsDashboardForm;
