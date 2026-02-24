import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";

type FormButtonsProps = {
  isLoading: boolean;
  onCancel: () => void;
};

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper mt={2} mb={2}>
      <ButtonLoader
        messageId="add"
        dataTestId="btn_add"
        color="primary"
        variant="contained"
        type="submit"
        startIcon={<AddOutlinedIcon fontSize="small" />}
        isLoading={isLoading}
        disabled={isRestricted}
        tooltip={{
          show: true,
          value: isRestricted ? restrictionReasonMessage : "add",
        }}
      />
      <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
