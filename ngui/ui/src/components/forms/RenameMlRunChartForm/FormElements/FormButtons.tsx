import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";

const FormButtons = () => (
  <FormButtonsWrapper>
    <ButtonLoader
      dataTestId="btn_rename_ml_run_chart"
      loaderDataTestId="loading_btn_rename_ml_run_chart"
      messageId="save"
      color="primary"
      variant="contained"
      type="submit"
    />
  </FormButtonsWrapper>
);

export default FormButtons;
