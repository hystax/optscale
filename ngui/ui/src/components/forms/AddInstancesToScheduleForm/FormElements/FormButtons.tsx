import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const FormButtons = ({ isLoading, onCancel }) => {
  const { isDemo } = useOrganizationInfo();

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
