import React from "react";
import { FormProvider } from "react-hook-form";
import { SETTINGS_TYPE_SUCCESS_MESSAGE, COMMON_YEAR_LENGTH } from "utils/constants";
import { lessOrEqual } from "utils/validation";
import BaseSideModal from "../BaseSideModal";
import { THRESHOLD_INPUT_NAMES } from "./components/constants";
import InformationWrapper from "./components/InformationWrapper";
import SaveButton from "./components/SaveButton";
import TextWithInlineInput from "./components/TextWithInlineInput";
import { useCommonSettingsData, useFormWithValuesFromOptions } from "./hooks";

const VALUE_KEYS = Object.freeze({
  [THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD]: "days_threshold",
  [THRESHOLD_INPUT_NAMES.CPU_PERCENT_THRESHOLD]: "cpu_percent_threshold",
  [THRESHOLD_INPUT_NAMES.NETWORK_BPS_THRESHOLD]: "network_bps_threshold"
});

const AbandonedInstancesThresholds = ({ recommendationType, onSuccess }) => {
  const { options, isGetDataLoading, isChangeSettingsAllowed, isSaveDataLoading, save } = useCommonSettingsData(
    recommendationType,
    SETTINGS_TYPE_SUCCESS_MESSAGE.THRESHOLDS,
    onSuccess
  );
  const { submitHandler, methods } = useFormWithValuesFromOptions(options, save, VALUE_KEYS);

  return (
    <FormProvider {...methods}>
      <form onSubmit={submitHandler}>
        <TextWithInlineInput
          messageId="thresholds.abandonedInstances.intro"
          isLoading={isGetDataLoading}
          lessOrEqualValidation={lessOrEqual(COMMON_YEAR_LENGTH)}
          name={THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD}
        />
        <ul>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedInstances.listItem1"
              name={THRESHOLD_INPUT_NAMES.CPU_PERCENT_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedInstances.listItem2"
              maxWidth="60px"
              name={THRESHOLD_INPUT_NAMES.NETWORK_BPS_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
        </ul>
        <SaveButton
          isGetDataLoading={isGetDataLoading}
          isChangeSettingsAllowed={isChangeSettingsAllowed}
          isSaveDataLoading={isSaveDataLoading}
        />
      </form>
    </FormProvider>
  );
};

class AbandonedInstancesModal extends BaseSideModal {
  headerProps = {
    messageId: "abandonedInstances",
    dataTestIds: {
      title: "lbl_abandoned_instances_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_abandoned_instances_strategy";

  get content() {
    return (
      <InformationWrapper>
        <AbandonedInstancesThresholds recommendationType={this.payload?.recommendationType} onSuccess={this.closeSideModal} />
      </InformationWrapper>
    );
  }
}

export default AbandonedInstancesModal;
