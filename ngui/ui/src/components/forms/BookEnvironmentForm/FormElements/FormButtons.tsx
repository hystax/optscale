import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";

const FormButtons = ({ isLoading, onCancel }) => (
  <FormButtonsWrapper>
    <ButtonLoader
      dataTestId="bnt_add"
      isLoading={isLoading}
      variant="contained"
      color="primary"
      messageId="book"
      type="submit"
    />
    <Button dataTestId="bnt_cancel" messageId="cancel" variant="outlined" onClick={onCancel} />
  </FormButtonsWrapper>
);

export default FormButtons;
