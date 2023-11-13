import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { updateResource } from "api";
import { UPDATE_RESOURCE } from "api/restapi/actionTypes";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const UnmarkEnvironmentContainer = ({ closeSideModal, resourceName, resourceId }) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_RESOURCE);

  const onSubmit = () =>
    dispatch((_, getState) => {
      dispatch(updateResource(resourceId, { shareable: false })).then(() => {
        if (!isError(UPDATE_RESOURCE, getState())) {
          closeSideModal();
        }
      });
    });

  return (
    <>
      <Box mb={2}>
        <Typography>
          <FormattedMessage
            id="unmarkEnvironmentInformation"
            values={{
              resourceName,
              strong: (chunks) => <strong>{chunks}</strong>
            }}
          />
        </Typography>
      </Box>
      <Box display="flex">
        <ButtonLoader color="error" messageId="unmark" variant="contained" onClick={onSubmit} isLoading={isLoading} />
        <Button messageId="cancel" variant="outlined" onClick={closeSideModal} />
      </Box>
    </>
  );
};

export default UnmarkEnvironmentContainer;
