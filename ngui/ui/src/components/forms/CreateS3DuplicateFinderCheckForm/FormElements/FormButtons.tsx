import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { FormButtonsProps } from "../types";

const FormButtons = ({ onCancel, isLoading = false }: FormButtonsProps) => {
  const { isDemo } = useOrganizationInfo();

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
        disabled={isDemo}
        tooltip={{
          show: isDemo,
          value: <FormattedMessage id="notAvailableInLiveDemo" />
        }}
      />
      <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
    </FormButtonsWrapper>
  );
};

export default FormButtons;
