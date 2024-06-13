import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { FormButtonsProps } from "../type";

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => (
  <FormButtonsWrapper>
    <ButtonLoader
      dataTestId="btn_update_data_source_sku"
      loaderDataTestId="loading_btn_update_data_source_sku"
      messageId="save"
      color="primary"
      variant="contained"
      type="submit"
      isLoading={isLoading}
    />
    <Button dataTestId="btn_cancel_update_data_source_sku" messageId="cancel" onClick={onCancel} />
  </FormButtonsWrapper>
);

export default FormButtons;
