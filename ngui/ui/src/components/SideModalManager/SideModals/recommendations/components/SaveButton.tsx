import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";

const SaveButton = ({ isGetDataLoading, isSaveDataLoading, isChangeSettingsAllowed }) => (
  <FormButtonsWrapper withBottomMargin>
    <ButtonLoader
      messageId="save"
      variant="contained"
      color="primary"
      tooltip={{
        show: !isChangeSettingsAllowed,
        messageId: "youDoNotHaveEnoughPermissions"
      }}
      type="submit"
      isLoading={isGetDataLoading || isSaveDataLoading}
    />
  </FormButtonsWrapper>
);

export default SaveButton;
