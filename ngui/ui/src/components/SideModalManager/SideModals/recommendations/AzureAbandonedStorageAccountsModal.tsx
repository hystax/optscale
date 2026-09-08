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
  [THRESHOLD_INPUT_NAMES.IDLE_DAYS_WINDOW]: "idle_days_window",
  [THRESHOLD_INPUT_NAMES.IDLE_TRANSACTIONS_THRESHOLD]: "idle_transactions_threshold",
  [THRESHOLD_INPUT_NAMES.MIN_ACCOUNT_AGE_DAYS]: "min_account_age_days",
  [THRESHOLD_INPUT_NAMES.MIN_USED_CAPACITY_GB]: "min_used_capacity_gb",
});

const AzureAbandonedStorageAccountsForm = ({ recommendationType, onSuccess }) => {
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
          messageId="thresholds.azureAbandonedStorageAccounts.intro"
          isLoading={isGetDataLoading}
          lessOrEqualValidation={lessOrEqual(COMMON_YEAR_LENGTH)}
          name={THRESHOLD_INPUT_NAMES.IDLE_DAYS_WINDOW}
        />
        <ul>
          <li>
            <TextWithInlineInput
              messageId="thresholds.azureAbandonedStorageAccounts.transactionsThreshold"
              name={THRESHOLD_INPUT_NAMES.IDLE_TRANSACTIONS_THRESHOLD}
              isLoading={isGetDataLoading}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.azureAbandonedStorageAccounts.minAccountAgeDays"
              isLoading={isGetDataLoading}
              name={THRESHOLD_INPUT_NAMES.MIN_ACCOUNT_AGE_DAYS}
            />
          </li>
          <li>
            <TextWithInlineInput
              messageId="thresholds.azureAbandonedStorageAccounts.minUsedCapacityGb"
              name={THRESHOLD_INPUT_NAMES.MIN_USED_CAPACITY_GB}
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

class AzureAbandonedStorageAccountsModal extends BaseSideModal {
  headerProps = {
    messageId: "azureAbandonedStorageAccounts",
    dataTestIds: {
      title: "lbl_azure_abandoned_storage_accounts_sidemodal_title",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_azure_abandoned_storage_accounts";

  get content() {
    return (
      <InformationWrapper>
        <AzureAbandonedStorageAccountsForm
          recommendationType={this.payload?.recommendationType}
          onSuccess={this.closeSideModal}
        />
      </InformationWrapper>
    );
  }
}

export default AzureAbandonedStorageAccountsModal;
