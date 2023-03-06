import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
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
          onClick={(event) => onDelete(event)}
          disabled={deleteButtonDisabled}
          isLoading={isLoading}
          tooltip={tooltip}
        />
        <Button
          dataTestId={cancelButtonDataTestId}
          messageId="cancel"
          variant="outlined"
          onClick={(event) => onCancel(event)}
        />
      </Box>
    </>
  );
};

DeleteEntity.propTypes = {
  onCancel: PropTypes.func.isRequired,
  message: PropTypes.exact({
    messageId: PropTypes.string.isRequired,
    values: PropTypes.object
  }),
  children: PropTypes.node,
  deleteButtonProps: PropTypes.exact({
    messageId: PropTypes.string,
    color: PropTypes.string,
    variant: PropTypes.string,
    disabled: PropTypes.bool,
    onDelete: PropTypes.func.isRequired,
    tooltip: PropTypes.object
  }).isRequired,
  dataTestIds: PropTypes.object,
  isLoading: PropTypes.bool
};

export default DeleteEntity;
