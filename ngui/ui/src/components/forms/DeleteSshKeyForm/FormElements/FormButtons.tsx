import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";

const FormButtons = ({ onClose, isLoading = false }) => (
  <FormButtonsWrapper>
    <ButtonLoader messageId="delete" color="error" variant="contained" type="submit" isLoading={isLoading} />
    <Button messageId="cancel" dataTestId="btn_cancel" onClick={onClose} />
  </FormButtonsWrapper>
);

export default FormButtons;
