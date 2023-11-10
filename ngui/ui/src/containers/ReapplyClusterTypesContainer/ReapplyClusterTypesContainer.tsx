import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { applyClusterTypes } from "api";
import { APPLY_CLUSTER_TYPES } from "api/restapi/actionTypes";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const ReapplyClusterTypesContainer = ({ onCancel }) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();

  const { isLoading: isClustersApplyLoading } = useApiState(APPLY_CLUSTER_TYPES);

  const onSuccess = onCancel;

  const onSubmit = () =>
    dispatch((_, getState) => {
      dispatch(applyClusterTypes(organizationId)).then(() => {
        if (!isError(APPLY_CLUSTER_TYPES, getState())) {
          onSuccess();
        }
      });
    });

  return (
    <>
      <Box mb={2}>
        <Typography data-test-id="p_re_apply">
          <FormattedMessage id="reapplyClusterTypesDescription" />
        </Typography>
      </Box>
      <Box display="flex">
        <ButtonLoader
          color="primary"
          messageId="run"
          dataTestId="btn_run"
          variant="contained"
          onClick={onSubmit}
          isLoading={isClustersApplyLoading}
        />
        <Button dataTestId="btn_cancel" messageId="cancel" variant="outlined" onClick={onCancel} />
      </Box>
    </>
  );
};

export default ReapplyClusterTypesContainer;
