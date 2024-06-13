import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";

const FormButtons = ({ isLoading = false }) => (
  <FormButtonsWrapper>
    <SubmitButtonLoader
      messageId="add"
      isLoading={isLoading}
      dataTestId="btn_create_key"
      loaderDataTestId="btn_create_key_loader"
    />
  </FormButtonsWrapper>
);

export default FormButtons;
