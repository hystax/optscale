import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { FormButtonsProps } from "../types";

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => (
  <FormButtonsWrapper>
    <SubmitButtonLoader
      messageId="create"
      isLoading={isLoading}
      dataTestId="btn_create_organization_option"
      loaderDataTestId="btn_create_organization_option_loader"
    />
    <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
  </FormButtonsWrapper>
);

export default FormButtons;
