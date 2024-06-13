import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";

const FormButtons = ({ isLoading = false }) => (
  <FormButtonsWrapper mt={1}>
    <ButtonLoader
      isLoading={isLoading}
      variant="contained"
      messageId="save"
      color="primary"
      type="submit"
      dataTestId="btn_save"
    />
  </FormButtonsWrapper>
);

export default FormButtons;
