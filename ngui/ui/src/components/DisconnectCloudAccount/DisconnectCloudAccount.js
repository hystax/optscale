import React from "react";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import DeleteEntity from "components/DeleteEntity";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { useDataSources } from "hooks/useDataSources";
import { AZURE_TENANT } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import Survey from "./Survey";

const DisconnectCloudAccount = ({ type, parentId, onCancel, isLoading, isLastDataSource = false }) => {
  const { disconnectQuestionId } = useDataSources(type);
  const isAzureTenant = type === AZURE_TENANT;

  return (
    <>
      {(parentId || isAzureTenant) && (
        <Box mb={SPACING_1}>
          {parentId && <InlineSeverityAlert messageId="childDataSourceDisconnectionWarning" />}
          {isAzureTenant && <InlineSeverityAlert messageId="parentDataSourceDisconnectionWarning" />}
        </Box>
      )}
      <DeleteEntity
        message={{
          messageId: isLastDataSource ? undefined : disconnectQuestionId
        }}
        dataTestIds={{
          text: "p_disconnect",
          cancelButton: "btn_cancel",
          deleteButton: "btn_disconnect_data_source"
        }}
        isLoading={isLoading}
        deleteButtonProps={{
          messageId: "disconnect"
        }}
        onCancel={onCancel}
      >
        {isLastDataSource && <Survey />}
      </DeleteEntity>
    </>
  );
};

DisconnectCloudAccount.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  onSubmit: PropTypes.func,
  onCancel: PropTypes.func.isRequired,
  type: PropTypes.string.isRequired,
  parentId: PropTypes.string,
  isLastDataSource: PropTypes.bool
};

export default DisconnectCloudAccount;
