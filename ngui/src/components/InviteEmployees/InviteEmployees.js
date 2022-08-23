import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import InviteEmployeesForm from "components/InviteEmployeesForm";
import PageContentWrapper from "components/PageContentWrapper";
import WrapperCard from "components/WrapperCard";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import { USER_MANAGEMENT } from "urls";

const actionBarDefinition = {
  goBack: true,
  title: {
    text: <FormattedMessage id="inviteUsersTitle" />,
    dataTestId: "lbl_users_invitation"
  }
};

const InviteEmployees = ({ onSubmit, availablePools, isLoadingProps = {} }) => {
  const isUpXl = useIsUpMediaQuery("xl");

  const navigate = useNavigate();

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <WrapperCard className={isUpXl ? "halfWidth" : ""}>
          <InviteEmployeesForm
            availablePools={availablePools}
            onSubmit={onSubmit}
            onCancel={() => navigate(USER_MANAGEMENT)}
            isLoadingProps={isLoadingProps}
          />
        </WrapperCard>
      </PageContentWrapper>
    </>
  );
};

InviteEmployees.propTypes = {
  onSubmit: PropTypes.func,
  availablePools: PropTypes.array,
  isLoadingProps: PropTypes.object
};

export default InviteEmployees;
