import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { FormButtonsProps } from "../types";

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => (
  <FormButtonsWrapper>
    <ButtonLoader
      dataTestId="btn_create_new_organization"
      messageId="create"
      color="primary"
      variant="contained"
      isLoading={isLoading}
      type="submit"
    />
    <Button dataTestId="btn_cancel_cloud_account" messageId="cancel" onClick={onCancel} />
  </FormButtonsWrapper>
);

export default FormButtons;
