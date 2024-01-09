import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";

type FormButtonsProps = {
  isLoading?: boolean;
};

const FormButtons = ({ isLoading = false }: FormButtonsProps) => (
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
