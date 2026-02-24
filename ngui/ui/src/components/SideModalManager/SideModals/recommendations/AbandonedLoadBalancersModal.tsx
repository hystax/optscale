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
  [THRESHOLD_INPUT_NAMES.BYTES_SENT_THRESHOLD]: "bytes_sent_threshold",
  [THRESHOLD_INPUT_NAMES.PACKETS_SENT_THRESHOLD]: "packets_sent_threshold",
  [THRESHOLD_INPUT_NAMES.REQUESTS_THRESHOLD]: "requests_threshold",
});

const AbandonedLoadBalancersThresholds = ({ recommendationType, onSuccess }) => {
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
          messageId="thresholds.abandonedLoadBalancers.intro"
          isLoading={isGetDataLoading}
          lessOrEqualValidation={lessOrEqual(COMMON_YEAR_LENGTH)}
          name={THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD}
        />
        <ul>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedLoadBalancers.1.bytesSentThreshold"
              name={THRESHOLD_INPUT_NAMES.BYTES_SENT_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedLoadBalancers.2.packetsSentThreshold"
              name={THRESHOLD_INPUT_NAMES.PACKETS_SENT_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedLoadBalancers.3.requestsThreshold"
              name={THRESHOLD_INPUT_NAMES.REQUESTS_THRESHOLD}
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

class AbandonedLoadBalancersModal extends BaseSideModal {
  headerProps = {
    messageId: "abandonedLoadBalancers",
    dataTestIds: {
      title: "lbl_abandoned_load_balancers_sidemodal_title",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_abandoned_load_balancers";

  get content() {
    return (
      <InformationWrapper>
        <AbandonedLoadBalancersThresholds
          recommendationType={this.payload?.recommendationType}
          onSuccess={this.closeSideModal}
        />
      </InformationWrapper>
    );
  }
}

export default AbandonedLoadBalancersModal;
