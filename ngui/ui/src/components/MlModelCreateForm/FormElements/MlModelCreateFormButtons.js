import React from "react";
import PropTypes from "prop-types";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const MlModelCreateFormButtons = ({ onCancel, isLoading = false }) => {
  const { isDemo } = useOrganizationInfo();

  return (
    <FormButtonsWrapper>
      <ButtonLoader
        messageId="save"
        dataTestId="btn_save"
        color="primary"
        variant="contained"
        type="submit"
        disabled={isDemo}
        tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
        isLoading={isLoading}
      />
      <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

MlModelCreateFormButtons.propTypes = {
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default MlModelCreateFormButtons;
