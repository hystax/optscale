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
  [THRESHOLD_INPUT_NAMES.DATA_SIZE_THRESHOLD]: "data_size_threshold",
  [THRESHOLD_INPUT_NAMES.TIER_1_REQUESTS_QUANTITY_THRESHOLD]: "tier_1_request_quantity_threshold",
  [THRESHOLD_INPUT_NAMES.TIER_2_REQUESTS_QUANTITY_THRESHOLD]: "tier_2_request_quantity_threshold"
});

const AbandonedS3BucketsForm = ({ recommendationType, onSuccess }) => {
  const { options, isGetDataLoading, isChangeSettingsAllowed, isSaveDataLoading, save } = useCommonSettingsData(
    recommendationType,
    SETTINGS_TYPE_SUCCESS_MESSAGE.THRESHOLDS,
    onSuccess
  );
  const { submitHandler, methods } = useFormWithValuesFromOptions(options, save, VALUE_KEYS);

  return (
    <FormProvider {...methods}>
      <form noValidate onSubmit={submitHandler}>
        <TextWithInlineInput
          messageId={"thresholds.abandonedS3Buckets.intro"}
          isLoading={isGetDataLoading}
          lessOrEqualValidation={lessOrEqual(COMMON_YEAR_LENGTH)}
          name={THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD}
        />
        <ul>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedS3Buckets.dataSizeThreshold"
              name={THRESHOLD_INPUT_NAMES.DATA_SIZE_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedS3Buckets.tier1RequestsQuantityThreshold"
              maxWidth="60px"
              name={THRESHOLD_INPUT_NAMES.TIER_1_REQUESTS_QUANTITY_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedS3Buckets.getRequestsQuantityThreshold"
              maxWidth="60px"
              name={THRESHOLD_INPUT_NAMES.TIER_2_REQUESTS_QUANTITY_THRESHOLD}
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

class AbandonedS3BucketsModal extends BaseSideModal {
  headerProps = {
    messageId: "abandonedS3Buckets",
    dataTestIds: {
      title: "lbl_abandoned_s3_buckets_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_abandoned_s3_buckets";

  get content() {
    return (
      <InformationWrapper>
        <AbandonedS3BucketsForm recommendationType={this.payload?.recommendationType} onSuccess={this.closeSideModal} />
      </InformationWrapper>
    );
  }
}

export default AbandonedS3BucketsModal;
