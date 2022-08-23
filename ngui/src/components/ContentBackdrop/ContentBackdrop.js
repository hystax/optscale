import React from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Backdrop from "components/Backdrop";
import Button from "components/Button";
import { useAllowedItems } from "hooks/useAllowedActions";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import AssignmentRuleIcon from "icons/AssignmentRuleIcon";
import DataSourceIcon from "icons/DataSourceIcon";
import EnvironmentIcon from "icons/EnvironmentIcon";
import PoolLimitIcon from "icons/PoolLimitIcon";
import {
  ASSIGNMENT_RULE_CREATE,
  ENVIRONMENT_CREATE,
  CLOUD_ACCOUNT_CONNECT,
  getEditPoolUrl,
  CLOUD_ACCOUNT_CONNECT_K8S
} from "urls";
import { isEmpty } from "utils/arrays";
import useStyles from "./ContentBackdrop.styles";

const CONNECT_DATA_SOURCE = "connectDataSource";
const ADD_ENVIRONMENT = "addEnvironment";
const SET_POOL = "setPoolLimit";
const CLOUD_CONNECTION_BACKDROP_MESSAGE = "cloudConnectionBackdropMessage";

const MESSAGE_TYPES = Object.freeze({
  ASSIGNMENT_RULES: "assignmentRules",
  CLOUD_ACCOUNTS: "cloudAccounts",
  K8S_RIGHTSIZING: "k8sRightsizing",
  RECOMMENDATIONS: "recommendations",
  POOLS: "pools",
  ENVIRONMENTS: "environments",
  DASHBOARD: "dashboard"
});

const redirectToCreateCloudAccount = (navigate) => navigate(CLOUD_ACCOUNT_CONNECT);
const redirectToCreateK8sAccount = (navigate) => navigate(CLOUD_ACCOUNT_CONNECT_K8S);
const redirectToEditPool = (navigate, poolId) => navigate(getEditPoolUrl(poolId));
const redirectToCreateRule = (navigate) => navigate(ASSIGNMENT_RULE_CREATE);
const redirectToCreateEnvironment = (navigate) => navigate(ENVIRONMENT_CREATE);

const getConfiguration = (messageType) =>
  ({
    cloudAccounts: {
      item: {
        requiredActions: ["MANAGE_CLOUD_CREDENTIALS"],
        mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "dataSourcesBackdropMessage"],
        buttonMessageId: CONNECT_DATA_SOURCE,
        subMessageIds: [CLOUD_CONNECTION_BACKDROP_MESSAGE],
        onButtonClick: redirectToCreateCloudAccount,
        dataTestIds: {
          mainMessage: ["p_sample", "p_connect_ca"],
          button: "btn_connect_ca",
          wrapper: "banner_mockup",
          img: "img_connect_data_source",
          subMessage: ["p_connection"]
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "dataSourcesContactManagerBackdropMessage"]
        },
        Icon: DataSourceIcon
      }
    },
    dashboard: {
      item: {
        requiredActions: ["MANAGE_CLOUD_CREDENTIALS", "MANAGE_RESOURCES"],
        mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "dashboardBackdropMessage"],
        // TODO: generalize approach to render buttons
        // currently we support 2 types of definition: array and plain properties
        buttons: [
          {
            messageId: ADD_ENVIRONMENT,
            onClick: redirectToCreateEnvironment,
            dataTestId: "btn_add_env"
          },
          {
            messageId: CONNECT_DATA_SOURCE,
            onClick: redirectToCreateCloudAccount,
            dataTestId: "btn_connect_ca"
          }
        ],
        dataTestIds: {
          mainMessage: ["p_sample", "p_connect_ca"],
          wrapper: "banner_mockup",
          img: "img_connect_data_source",
          subMessage: ["p_connection"]
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "dashboardContactManagerBackdropMessage"]
        },
        Icon: DataSourceIcon
      }
    },
    recommendations: {
      item: {
        requiredActions: ["MANAGE_CLOUD_CREDENTIALS"],
        mainMessageIds: ["recommendationsBackdropMessage"],
        buttonMessageId: CONNECT_DATA_SOURCE,
        subMessageIds: [CLOUD_CONNECTION_BACKDROP_MESSAGE],
        onButtonClick: redirectToCreateCloudAccount,
        dataTestIds: {
          mainMessage: ["p_connect_ca"],
          button: "btn_connect_ca",
          subMessage: ["p_connection"]
        },
        renderIfNotAllowed: {
          mainMessageIds: ["recommendationsContactManagerBackdropMessage"]
        },
        Icon: DataSourceIcon
      }
    },
    pools: {
      item: {
        requiredActions: ["MANAGE_POOLS"],
        mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "poolsBackdropMessage"],
        buttonMessageId: SET_POOL,
        onButtonClick: redirectToEditPool,
        dataTestIds: {
          mainMessage: ["p_sample", "p_set_pool"],
          button: "btn_set_pool",
          wrapper: "banner_mockup",
          img: "img_set_pool_limit"
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "poolsContactManagerBackdropMessage"]
        },
        Icon: PoolLimitIcon
      }
    },
    assignmentRules: {
      item: {
        mainMessageIds: ["youDontHaveAnyAutomaticAssignmentRulesCreatedYet", "createAutomaticAssignmentRuleBackdropMessage"],
        buttonMessageId: "add",
        onButtonClick: redirectToCreateRule,
        dataTestIds: {
          mainMessage: ["p_no_automatic_rules", "p_add_an_assignment_rule"],
          button: "btn_add_rule",
          wrapper: "banner_mockup",
          img: "img_add_rule"
        },
        Icon: AssignmentRuleIcon
      }
    },
    environments: {
      item: {
        requiredActions: ["MANAGE_RESOURCES"],
        mainMessageIds: ["youDontHaveAnyEnvironmentsCreatedYet", "createEnvironmentsBackdropMessage"],
        buttonMessageId: "add",
        onButtonClick: redirectToCreateEnvironment,
        dataTestIds: {
          mainMessage: ["p_sample", "p_add_env"],
          button: "btn_add_env",
          wrapper: "banner_mockup",
          img: "img_add_env"
        },
        renderIfNotAllowed: {
          mainMessageIds: ["youDontHaveAnyEnvironmentsCreatedYet", "environmentsContactManagerBackdropMessage"]
        },
        Icon: EnvironmentIcon
      }
    },
    k8sRightsizing: {
      item: {
        requiredActions: ["MANAGE_CLOUD_CREDENTIALS"],
        mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "k8sBackdropMessage"],
        buttonMessageId: CONNECT_DATA_SOURCE,
        subMessageIds: [CLOUD_CONNECTION_BACKDROP_MESSAGE],
        onButtonClick: redirectToCreateK8sAccount,
        dataTestIds: {
          mainMessage: ["p_sample", "p_connect_ca"],
          button: "btn_connect_ca",
          wrapper: "banner_mockup",
          img: "img_connect_data_source",
          subMessage: ["p_connection"]
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "dataSourcesContactManagerBackdropMessage"]
        },
        Icon: DataSourceIcon
      }
    }
  }[messageType]);

const ContentBackdrop = ({ messageType, children }) => {
  const { classes, cx } = useStyles();
  const { organizationPoolId } = useOrganizationInfo();

  const navigate = useNavigate();

  const renderTypography = (messageIds, messageDataTestIds, isSubMessage = false) =>
    messageIds.map((messageId, index, sourceArray) => {
      const isLastTypography = index === sourceArray.length - 1;
      return (
        <Typography
          data-test-id={messageDataTestIds ? messageDataTestIds[index] : null}
          key={messageId}
          variant={isSubMessage ? "caption" : null}
          className={isSubMessage ? "" : classes.bold}
          paragraph={isLastTypography && !isSubMessage}
          align="center"
          gutterBottom
        >
          <FormattedMessage id={messageId} />
        </Typography>
      );
    });

  const { item = {} } = getConfiguration(messageType);
  const { Icon } = item;
  const [{ mainMessageIds = [], buttons, buttonMessageId, subMessageIds = [], onButtonClick, dataTestIds = {} } = {}] =
    useAllowedItems({
      items: [item]
    });

  return (
    <>
      <Paper data-test-id={dataTestIds.wrapper} variant="elevation" elevation={3} className={classes.root}>
        {Icon && <Icon data-test-id={dataTestIds.img} className={classes.icon} />}
        {!isEmpty(mainMessageIds) ? renderTypography(mainMessageIds, dataTestIds.mainMessage) : null}
        {buttonMessageId && (
          <Button
            dataTestId={dataTestIds.button}
            customClass={!isEmpty(subMessageIds) ? classes.buttonMargin : ""}
            size="medium"
            variant="contained"
            color="success"
            onClick={() => onButtonClick(navigate, organizationPoolId)}
            messageId={buttonMessageId}
          />
        )}
        {Array.isArray(buttons) && (
          <div className={cx(classes.buttonsWrapper, !isEmpty(subMessageIds) ? classes.buttonsWrapperMargin : "")}>
            {buttons.map(({ messageId, dataTestId, onClick }) => (
              <Button
                key={messageId}
                messageId={messageId}
                customClass={classes.buttonWidth}
                onClick={() => onClick(navigate, organizationPoolId)}
                dataTestId={dataTestId}
                size="medium"
                variant="contained"
                color="success"
              />
            ))}
          </div>
        )}
        {!isEmpty(subMessageIds) && renderTypography(subMessageIds, dataTestIds.subMessage, true)}
      </Paper>
      <Box height="100%" position="relative">
        <Backdrop customClass="content" />
        {children}
      </Box>
    </>
  );
};

ContentBackdrop.propTypes = {
  messageType: PropTypes.oneOf([
    MESSAGE_TYPES.ASSIGNMENT_RULES,
    MESSAGE_TYPES.CLOUD_ACCOUNTS,
    MESSAGE_TYPES.RECOMMENDATIONS,
    MESSAGE_TYPES.POOLS,
    MESSAGE_TYPES.ENVIRONMENTS,
    MESSAGE_TYPES.DASHBOARD,
    MESSAGE_TYPES.K8S_RIGHTSIZING
  ]).isRequired,
  isFixed: PropTypes.bool,
  children: PropTypes.node
};

export default ContentBackdrop;
export { MESSAGE_TYPES };
