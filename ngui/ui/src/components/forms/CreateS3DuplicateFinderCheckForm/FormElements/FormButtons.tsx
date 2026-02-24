import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { FormButtonsProps } from "../types";

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  return (
    <FormButtonsWrapper>
      <ButtonLoader
        messageId="run"
        dataTestId="btn_run"
        color="primary"
        variant="contained"
        type="submit"
        startIcon={<PlayCircleOutlineIcon fontSize="small" />}
        isLoading={isLoading}
        disabled={isRestricted}
        tooltip={{
          show: isRestricted,
          value: restrictionReasonMessage,
        }}
      />
      <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
