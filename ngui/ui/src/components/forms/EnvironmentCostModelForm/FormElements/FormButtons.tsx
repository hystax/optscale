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
    <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
  </FormButtonsWrapper>
);

export default FormButtons;
