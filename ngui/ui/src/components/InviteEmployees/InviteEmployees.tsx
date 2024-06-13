import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import InviteEmployeesForm from "components/forms/InviteEmployeesForm";
import PageContentWrapper from "components/PageContentWrapper";
import { USER_MANAGEMENT } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={USER_MANAGEMENT} component={RouterLink}>
      <FormattedMessage id="users" />
    </Link>
  ],
  title: {
    text: <FormattedMessage id="inviteUsersTitle" />,
    dataTestId: "lbl_users_invitation"
  }
};

const InviteEmployees = ({ onSubmit, availablePools, isLoadingProps = {} }) => {
  const navigate = useNavigate();

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Box sx={{ width: { xl: "50%" } }}>
          <InviteEmployeesForm
            availablePools={availablePools}
            onSubmit={onSubmit}
            onCancel={() => navigate(USER_MANAGEMENT)}
            isLoadingProps={isLoadingProps}
          />
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default InviteEmployees;
