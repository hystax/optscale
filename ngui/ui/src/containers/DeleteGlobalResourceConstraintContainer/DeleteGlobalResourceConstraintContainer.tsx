import { Typography } from "@mui/material";
import { Box } from "@mui/system";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { deleteGlobalResourceConstraint } from "api";
import { DELETE_GLOBAL_RESOURCE_CONSTRAINT } from "api/restapi/actionTypes";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import { useApiState } from "hooks/useApiState";
import { checkError } from "utils/api";
import { CONSTRAINTS_TYPES } from "utils/constraints";

const DeleteGlobalResourceConstraintContainer = ({
  constraintId,
  constraintType,
  resourceName,
  cloudResourceId,
  closeSideModal
}) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(DELETE_GLOBAL_RESOURCE_CONSTRAINT);

  const onSubmit = () => {
    dispatch((_, getState) => {
      dispatch(deleteGlobalResourceConstraint(constraintId))
        .then(() => checkError(DELETE_GLOBAL_RESOURCE_CONSTRAINT, getState()))
        .then(() => {
          if (typeof closeSideModal === "function") {
            closeSideModal();
          }
        });
    });
  };

  return (
    <>
      <Box mb={2}>
        <Typography>
          <FormattedMessage
            id="deleteResourceConstraintQuestion"
            values={{
              type: <FormattedMessage id={CONSTRAINTS_TYPES[constraintType]} />,
              resourceName: resourceName || cloudResourceId,
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </Box>
      <Box display="flex">
        <ButtonLoader color="error" messageId="delete" variant="contained" onClick={onSubmit} isLoading={isLoading} />
        <Button messageId="cancel" variant="outlined" onClick={closeSideModal} />
      </Box>
    </>
  );
};

export default DeleteGlobalResourceConstraintContainer;
