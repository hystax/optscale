import React from "react";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Button from "components/Button";
import EnvironmentsTable from "components/EnvironmentsTable";
import WrapperCard from "components/WrapperCard";
import { useIsAllowed } from "hooks/useAllowedActions";
import EnvironmentIcon from "icons/EnvironmentIcon";
import { ENVIRONMENTS, ENVIRONMENT_CREATE } from "urls";
import { isEmpty } from "utils/arrays";
import useStyles from "./EnvironmentsCard.styles";

const AddEnvironment = () => {
  const { classes } = useStyles();

  const isManageResourcesAllowed = useIsAllowed({
    requiredActions: ["MANAGE_RESOURCES"]
  });

  return (
    <div className={classes.noEnvironmentsWrapper}>
      <EnvironmentIcon data-test-id="img_add_env" className={classes.icon} />
      <Typography paragraph align="center" gutterBottom data-test-id="p_sample">
        <FormattedMessage id="youDontHaveAnyEnvironmentsCreatedYet" />
      </Typography>
      <Typography paragraph align="center" gutterBottom data-test-id="p_add_env">
        <FormattedMessage
          id={isManageResourcesAllowed ? "createEnvironmentsBackdropMessage" : "environmentsContactManagerBackdropMessage"}
        />
      </Typography>
      {isManageResourcesAllowed && (
        <div>
          <Button
            size="medium"
            variant="contained"
            color="success"
            link={ENVIRONMENT_CREATE}
            messageId={"addEnvironment"}
            dataTestId="btn_add_env"
          />
        </div>
      )}
    </div>
  );
};

const EnvironmentsCard = ({ isLoading, environments }) => {
  const navigate = useNavigate();

  const goToEnvironments = () => navigate(ENVIRONMENTS);

  const renderLoader = () => (
    <EnvironmentsTable shortTable data={[]} isLoadingProps={{ isGetEnvironmentsLoading: isLoading }} />
  );

  const renderContent = () =>
    isEmpty(environments) ? (
      <AddEnvironment />
    ) : (
      <EnvironmentsTable shortTable data={environments} isLoadingProps={{ isGetEnvironmentsLoading: isLoading }} />
    );

  return (
    <WrapperCard
      needAlign
      title={<FormattedMessage id="environments" />}
      titleButton={{
        type: "icon",
        tooltip: {
          title: <FormattedMessage id="goToItEnvironments" />
        },
        buttonProps: {
          icon: <ExitToAppOutlinedIcon />,
          isLoading,
          onClick: goToEnvironments,
          dataTestId: "btn_go_to_environments"
        }
      }}
      dataTestIds={{
        wrapper: "block_environments",
        title: "lbl_environments"
      }}
      elevation={0}
    >
      {isLoading ? renderLoader() : renderContent()}
    </WrapperCard>
  );
};

EnvironmentsCard.propTypes = {
  environments: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default EnvironmentsCard;
