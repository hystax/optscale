import React, { useState } from "react";
import CreateOutlinedIcon from "@mui/icons-material/CreateOutlined";
import { Typography } from "@mui/material";
import { Box } from "@mui/system";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { ConstraintLimitMessage } from "components/ConstraintMessage";
import EditPoolPolicyLimitForm from "components/EditPoolPolicyLimitForm";
import IconButton from "components/IconButton";
import { CONSTRAINT_MESSAGE_FORMAT } from "utils/constraints";

export const MODE = Object.freeze({
  CREATE: "create",
  UPDATE: "update"
});

const EditablePoolPolicyLimit = ({
  isAllowedToEdit,
  policyId,
  policyLimit,
  policyType,
  formattedPolicyLimit,
  onSubmit,
  isLoading = false,
  dataTestIds = {}
}) => {
  const [editMode, setEditMode] = useState(false);

  const onEditMode = () => {
    setEditMode(true);
  };

  const offEditMode = () => {
    setEditMode(false);
  };

  const { constraintLimitMessageDataTestId, editButtonDataTestId } = dataTestIds;

  return editMode ? (
    <EditPoolPolicyLimitForm
      onSubmit={(formData) => {
        const limitNumber = Number(formData.limit);

        if (limitNumber === policyLimit) {
          offEditMode();
          return;
        }

        const formatFormData = () => {
          const formattedData = {
            ...formData,
            type: policyType,
            limit: Number.isInteger(limitNumber) ? limitNumber : undefined
          };

          if (policyId) {
            formattedData.policyId = policyId;
          }

          return formattedData;
        };

        const formattedData = formatFormData();

        const mode = policyId ? MODE.UPDATE : MODE.CREATE;

        onSubmit(mode, formattedData, { onSuccess: () => offEditMode() });
      }}
      policyType={policyType}
      policyLimit={policyLimit}
      isLoading={isLoading}
      onCancel={offEditMode}
    />
  ) : (
    <Box display="flex" alignItems="center">
      <Typography data-test-id={constraintLimitMessageDataTestId}>
        {policyLimit === undefined ? (
          <FormattedMessage id="notSet" />
        ) : (
          formattedPolicyLimit || (
            <ConstraintLimitMessage limit={policyLimit} type={policyType} formats={{ ttl: CONSTRAINT_MESSAGE_FORMAT.TEXT }} />
          )
        )}
      </Typography>
      {isAllowedToEdit && (
        <IconButton
          key="create"
          icon={<CreateOutlinedIcon />}
          onClick={() => onEditMode()}
          tooltip={{
            show: true,
            messageId: "edit"
          }}
          dataTestId={editButtonDataTestId}
        />
      )}
    </Box>
  );
};

EditablePoolPolicyLimit.propTypes = {
  isAllowedToEdit: PropTypes.bool.isRequired,
  policyType: PropTypes.string.isRequired,
  policyLimit: PropTypes.number,
  formattedPolicyLimit: PropTypes.string,
  policyId: PropTypes.string,
  onSubmit: PropTypes.func,
  isLoading: PropTypes.bool,
  dataTestIds: PropTypes.shape({
    constraintLimitMessageDataTestId: PropTypes.object,
    editButtonDataTestId: PropTypes.object
  })
};

export default EditablePoolPolicyLimit;
