import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";

const FormButtons = ({ isLoading = false }) => (
  <FormButtonsWrapper mt={3} mb={2}>
    <ButtonLoader
      uppercase
      fullWidth
      variant="contained"
      color="lightBlue"
      isLoading={isLoading}
      messageId="confirm"
      type="submit"
      size="large"
    />
  </FormButtonsWrapper>
);

export default FormButtons;
