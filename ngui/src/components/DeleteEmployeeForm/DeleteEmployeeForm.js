import React from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm, Controller } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import OrganizationLabel from "components/OrganizationLabel";
import Selector from "components/Selector";
import { EMPLOYEES_INVITE } from "urls";

const ORGANIZATION_MANAGER_ID = "organizationManagerId";

const DeleteEmployeeForm = ({
  closeSideModal,
  organizationName,
  entityToBeDeleted,
  organizationManagersWhoSuitableForAssignment,
  onSubmit,
  isDeletingMyself = false,
  isOnlyOneOrganizationManager = false,
  isLoading = false
}) => {
  const isYouAreOnlyOrganizationManager = isOnlyOneOrganizationManager && isDeletingMyself;

  const intl = useIntl();
  const methods = useForm();

  const {
    control,
    handleSubmit,
    formState: { errors }
  } = methods;

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      {!isYouAreOnlyOrganizationManager && (
        <>
          <Box mb={2}>
            <Typography gutterBottom>
              <FormattedMessage
                id="deleteUserDescription"
                values={{
                  userName: entityToBeDeleted.employeeName,
                  organizationName: <OrganizationLabel disableLink name={organizationName} />
                }}
              />
            </Typography>
          </Box>
          <Box mb={2}>
            <Typography gutterBottom>
              <FormattedMessage
                id="selectNewUserThatWillTakeOverAllAssets"
                values={{
                  userName: entityToBeDeleted.employeeName
                }}
              />
            </Typography>
          </Box>
          <Controller
            name={ORGANIZATION_MANAGER_ID}
            defaultValue=""
            control={control}
            rules={{
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              }
            }}
            render={({ field: controllerField }) => (
              <Selector
                required
                error={!!errors[ORGANIZATION_MANAGER_ID]}
                helperText={errors?.[ORGANIZATION_MANAGER_ID]?.message}
                data={{ items: organizationManagersWhoSuitableForAssignment }}
                labelId="organizationManagers"
                {...controllerField}
              />
            )}
          />
        </>
      )}
      {isYouAreOnlyOrganizationManager && (
        <Box mb={2}>
          <Typography color="error" gutterBottom>
            <FormattedMessage
              id="youAreOnlyOrganizationManager"
              values={{
                link: (chunks) => (
                  <Link to={EMPLOYEES_INVITE} component={RouterLink}>
                    {chunks}
                  </Link>
                )
              }}
            />
          </Typography>
        </Box>
      )}
      <FormButtonsWrapper>
        {!isYouAreOnlyOrganizationManager && (
          <ButtonLoader messageId="delete" color="error" variant="contained" type="submit" isLoading={isLoading} />
        )}
        <Button messageId="cancel" dataTestId="btn_cancel" onClick={closeSideModal} />
      </FormButtonsWrapper>
    </form>
  );
};

DeleteEmployeeForm.propTypes = {
  closeSideModal: PropTypes.func.isRequired,
  entityToBeDeleted: PropTypes.object.isRequired,
  organizationName: PropTypes.string.isRequired,
  organizationManagersWhoSuitableForAssignment: PropTypes.array.isRequired,
  onSubmit: PropTypes.func.isRequired,
  isDeletingMyself: PropTypes.bool,
  isOnlyOneOrganizationManager: PropTypes.bool,
  isLoading: PropTypes.bool,
  isOpen: PropTypes.bool
};

export default DeleteEmployeeForm;
