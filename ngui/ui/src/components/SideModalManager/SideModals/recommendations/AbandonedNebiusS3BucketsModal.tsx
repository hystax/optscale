import { FormProvider } from "react-hook-form";
import { COMMON_YEAR_LENGTH, SETTINGS_TYPE_SUCCESS_MESSAGE } from "utils/constants";
import { lessOrEqual } from "utils/validation";
import BaseSideModal from "../BaseSideModal";
import { THRESHOLD_INPUT_NAMES } from "./components/constants";
import SaveButton from "./components/SaveButton";
import TextWithInlineInput from "./components/TextWithInlineInput";
import { useCommonSettingsData, useFormWithValuesFromOptions } from "./hooks";

const VALUE_KEYS = Object.freeze({
  [THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD]: "days_threshold",
  [THRESHOLD_INPUT_NAMES.DATA_SIZE_THRESHOLD]: "data_size_threshold",
  [THRESHOLD_INPUT_NAMES.GET_REQUEST_QUANTITY_THRESHOLD]: "get_request_quantity_threshold",
  [THRESHOLD_INPUT_NAMES.POST_REQUEST_QUANTITY_THRESHOLD]: "post_request_quantity_threshold",
  [THRESHOLD_INPUT_NAMES.PUT_REQUEST_QUANTITY_THRESHOLD]: "put_request_quantity_threshold",
  [THRESHOLD_INPUT_NAMES.HEAD_REQUEST_QUANTITY_THRESHOLD]: "head_request_quantity_threshold",
  [THRESHOLD_INPUT_NAMES.OPTIONS_REQUEST_QUANTITY_THRESHOLD]: "options_request_quantity_threshold",
  [THRESHOLD_INPUT_NAMES.DELETE_REQUEST_QUANTITY_THRESHOLD]: "delete_request_quantity_threshold"
});

const AbandonedNebiusS3BucketsForm = ({ recommendationType, onSuccess }) => {
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
          messageId={"thresholds.abandonedNebiusS3Buckets.intro"}
          isLoading={isGetDataLoading}
          lessOrEqualValidation={lessOrEqual(COMMON_YEAR_LENGTH)}
          name={THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD}
        />
        <ul>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedNebiusS3Buckets.dataSizeThreshold"
              name={THRESHOLD_INPUT_NAMES.DATA_SIZE_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedNebiusS3Buckets.getRequestsQuantityThreshold"
              maxWidth="60px"
              name={THRESHOLD_INPUT_NAMES.GET_REQUEST_QUANTITY_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedNebiusS3Buckets.postRequestsQuantityThreshold"
              maxWidth="60px"
              name={THRESHOLD_INPUT_NAMES.POST_REQUEST_QUANTITY_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedNebiusS3Buckets.putRequestsQuantityThreshold"
              maxWidth="60px"
              name={THRESHOLD_INPUT_NAMES.PUT_REQUEST_QUANTITY_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedNebiusS3Buckets.headRequestsQuantityThreshold"
              maxWidth="60px"
              name={THRESHOLD_INPUT_NAMES.HEAD_REQUEST_QUANTITY_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedNebiusS3Buckets.optionsRequestsQuantityThreshold"
              maxWidth="60px"
              name={THRESHOLD_INPUT_NAMES.OPTIONS_REQUEST_QUANTITY_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.abandonedNebiusS3Buckets.deleteRequestsQuantityThreshold"
              maxWidth="60px"
              name={THRESHOLD_INPUT_NAMES.DELETE_REQUEST_QUANTITY_THRESHOLD}
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

class AbandonedNebiusS3BucketsModal extends BaseSideModal {
  headerProps = {
    messageId: "abandonedNebuisS3Buckets",
    dataTestIds: {
      title: "lbl_abandoned_nebuis_s3_buckets_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_abandoned_nebius_s3_buckets";

  get content() {
    return (
      <AbandonedNebiusS3BucketsForm recommendationType={this.payload?.recommendationType} onSuccess={this.closeSideModal} />
    );
  }
}

export default AbandonedNebiusS3BucketsModal;
