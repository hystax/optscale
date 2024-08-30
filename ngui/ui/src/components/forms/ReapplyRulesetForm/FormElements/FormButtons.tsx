import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";

const FormButtons = ({ onCancel, isLoading = false }) => (
  <FormButtonsWrapper>
    <ButtonLoader
      dataTestId="run_btn"
      messageId="run"
      color="primary"
      variant="contained"
      isLoading={isLoading}
      type="submit"
    />
    <Button dataTestId="cancel_btn" messageId="cancel" variant="outlined" onClick={onCancel} />
  </FormButtonsWrapper>
);

export default FormButtons;
