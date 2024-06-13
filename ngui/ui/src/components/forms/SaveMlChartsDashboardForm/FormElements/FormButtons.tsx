import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";

const FormButtons = ({ onCancel, isLoading = false }) => (
  <FormButtonsWrapper>
    <ButtonLoader
      isLoading={isLoading}
      variant="contained"
      messageId="save"
      color="primary"
      type="submit"
      dataTestId="btn_save"
    />
    <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
  </FormButtonsWrapper>
);

export default FormButtons;
