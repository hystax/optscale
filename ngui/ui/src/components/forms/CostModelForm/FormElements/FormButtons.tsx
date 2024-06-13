import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { FormButtonsProps } from "../types";

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => (
  <FormButtonsWrapper>
    <ButtonLoader
      isLoading={isLoading}
      variant="contained"
      color="primary"
      messageId="save"
      type="submit"
      loaderDataTestId="loading_btn_save"
      dataTestId="btn_save"
    />
    <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
  </FormButtonsWrapper>
);

export default FormButtons;
