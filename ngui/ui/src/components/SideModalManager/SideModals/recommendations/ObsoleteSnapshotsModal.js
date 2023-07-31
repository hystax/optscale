import React from "react";
import { Typography } from "@mui/material";
import { FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { SETTINGS_TYPE_SUCCESS_MESSAGE, COMMON_YEAR_LENGTH } from "utils/constants";
import { lessOrEqual } from "utils/validation";
import BaseSideModal from "../BaseSideModal";
import { THRESHOLD_INPUT_NAMES } from "./components/constants";
import InformationWrapper from "./components/InformationWrapper";
import SaveButton from "./components/SaveButton";
import TextWithInlineInput from "./components/TextWithInlineInput";
import { useCommonSettingsData, useFormWithValuesFromOptions } from "./hooks";

const VALUE_KEYS = Object.freeze({
  [THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD]: "days_threshold"
});

const ObsoleteSnapshotsThresholds = ({ recommendationType, onSuccess }) => {
  const { options, isGetDataLoading, isChangeSettingsAllowed, isSaveDataLoading, save } = useCommonSettingsData(
    recommendationType,
    SETTINGS_TYPE_SUCCESS_MESSAGE.THRESHOLDS,
    onSuccess
  );
  const { submitHandler, methods } = useFormWithValuesFromOptions(options, save, VALUE_KEYS);

  return (
    <FormProvider {...methods}>
      <form onSubmit={submitHandler}>
        <Typography component="div">
          <FormattedMessage id="thresholds.obsoleteSnapshots.title" />
          <ul>
            <li>
              <FormattedMessage id="thresholds.obsoleteSnapshots.listItem1" />
            </li>
            <li>
              <FormattedMessage id="thresholds.obsoleteSnapshots.listItem2" />
            </li>
            <li>
              <TextWithInlineInput
                messageId="thresholds.obsoleteSnapshots.listItem3"
                isLoading={isGetDataLoading}
                lessOrEqualValidation={lessOrEqual(COMMON_YEAR_LENGTH)}
                name={THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD}
              />
            </li>
          </ul>
        </Typography>
        <SaveButton
          isGetDataLoading={isGetDataLoading}
          isChangeSettingsAllowed={isChangeSettingsAllowed}
          isSaveDataLoading={isSaveDataLoading}
        />
      </form>
    </FormProvider>
  );
};

class ObsoleteSnapshotsModal extends BaseSideModal {
  headerProps = {
    messageId: "obsoleteSnapshots",
    dataTestIds: {
      title: "lbl_obsolete_snapshots_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_obsolete_snapshots";

  get content() {
    return (
      <InformationWrapper>
        <ObsoleteSnapshotsThresholds recommendationType={this.payload?.recommendationType} onSuccess={this.closeSideModal} />
      </InformationWrapper>
    );
  }
}

export default ObsoleteSnapshotsModal;
