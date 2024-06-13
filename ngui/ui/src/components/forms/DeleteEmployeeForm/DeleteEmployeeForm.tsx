import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import OrganizationLabel from "components/OrganizationLabel";
import { EMPLOYEES_INVITE } from "urls";
import { OrganizationManagerSelector } from "./FormElements";
import { DeleteEmployeeFormProps, FormValues } from "./types";

const DeleteEmployeeForm = ({
  closeSideModal,
  organizationName,
  entityToBeDeleted,
  organizationManagersWhoSuitableForAssignment,
  onSubmit,
  isDeletingMyself = false,
  isOnlyOneOrganizationManager = false,
  isLoading = false
}: DeleteEmployeeFormProps) => {
  const isYouAreOnlyOrganizationManager = isOnlyOneOrganizationManager && isDeletingMyself;

  const methods = useForm<FormValues>();

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
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
            <OrganizationManagerSelector
              organizationManagersWhoSuitableForAssignment={organizationManagersWhoSuitableForAssignment}
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
    </FormProvider>
  );
};

export default DeleteEmployeeForm;
