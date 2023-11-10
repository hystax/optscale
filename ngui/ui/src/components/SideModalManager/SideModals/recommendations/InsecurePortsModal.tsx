import { Controller, FormProvider } from "react-hook-form";
import { SETTINGS_TYPE_SUCCESS_MESSAGE } from "utils/constants";
import BaseSideModal from "../BaseSideModal";
import InformationWrapper from "./components/InformationWrapper";
import InsecurePorts from "./components/InsecurePorts";
import SaveButton from "./components/SaveButton";
import { useCommonSettingsData, useFormWithValuesFromOptions } from "./hooks";

const VALUE_KEYS = Object.freeze({
  insecurePorts: "insecure_ports"
});

const InsecurePortsForm = ({ recommendationType, onSuccess }) => {
  const { options, isGetDataLoading, isChangeSettingsAllowed, isSaveDataLoading, save } = useCommonSettingsData(
    recommendationType,
    SETTINGS_TYPE_SUCCESS_MESSAGE.INSECURE_PORTS,
    onSuccess
  );
  const { submitHandler, methods } = useFormWithValuesFromOptions(options, save, VALUE_KEYS);
  const { control } = methods;

  return (
    <FormProvider {...methods}>
      <form noValidate onSubmit={submitHandler}>
        <Controller
          name="insecurePorts"
          control={control}
          render={({ field: { onChange, value } }) => (
            <InsecurePorts
              insecurePorts={value}
              setData={(ports) => {
                onChange(ports);
              }}
              isLoading={isGetDataLoading}
              isChangeSettingsAllowed={isChangeSettingsAllowed}
            />
          )}
        />
        <SaveButton
          isGetDataLoading={isGetDataLoading}
          isChangeSettingsAllowed={isChangeSettingsAllowed}
          isSaveDataLoading={isSaveDataLoading}
        />
      </form>
    </FormProvider>
  );
};

class InsecurePortsModal extends BaseSideModal {
  headerProps = {
    messageId: "insecurePorts",
    dataTestIds: {
      title: "lbl_insecure_ports_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_insecure_ports";

  get content() {
    return (
      <InformationWrapper>
        <InsecurePortsForm recommendationType={this.payload?.recommendationType} onSuccess={this.closeSideModal} />
      </InformationWrapper>
    );
  }
}

export default InsecurePortsModal;
