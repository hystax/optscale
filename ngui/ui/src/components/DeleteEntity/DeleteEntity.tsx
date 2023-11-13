import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";

const DeleteEntity = ({ children, onCancel, message = {}, dataTestIds, isLoading = false, deleteButtonProps = {} }) => {
  const {
    text: textDataTestId,
    deleteButton: deleteButtonDataTestId,
    cancelButton: cancelButtonDataTestId
  } = dataTestIds || {};
  const { messageId, values = {} } = message;
  const {
    disabled: deleteButtonDisabled = false,
    messageId: deleteButtonMessageId = "delete",
    color: deleteButtonColor = "error",
    variant: deleteButtonVariant = "contained",
    tooltip,
    onDelete
  } = deleteButtonProps;

  return (
    <>
      {messageId && (
        <Box mb={2}>
          <Typography data-test-id={textDataTestId}>
            <FormattedMessage id={messageId} values={values} />
          </Typography>
        </Box>
      )}
      {children ? <Box mb={2}>{children}</Box> : null}
      <Box display="flex" mr={2}>
        <ButtonLoader
          dataTestId={deleteButtonDataTestId}
          messageId={deleteButtonMessageId}
          color={deleteButtonColor}
          variant={deleteButtonVariant}
          onClick={typeof onDelete === "function" ? onDelete : undefined}
          disabled={deleteButtonDisabled}
          isLoading={isLoading}
          tooltip={tooltip}
          type="submit"
        />
        <Button dataTestId={cancelButtonDataTestId} messageId="cancel" variant="outlined" onClick={onCancel} />
      </Box>
    </>
  );
};

export default DeleteEntity;
