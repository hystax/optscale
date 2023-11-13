import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import Button from "components/Button";
import EditPoolModal from "components/SideModalManager/SideModals/EditPoolModal";
import { useAllowedItems } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import AssignmentRuleIcon from "icons/AssignmentRuleIcon";
import DataSourceIcon from "icons/DataSourceIcon";
import EnvironmentIcon from "icons/EnvironmentIcon";
import PoolLimitIcon from "icons/PoolLimitIcon";
import {
  ASSIGNMENT_RULE_CREATE,
  ENVIRONMENT_CREATE,
  CLOUD_ACCOUNT_CONNECT,
  CLOUD_ACCOUNT_CONNECT_K8S,
  ANOMALY_CREATE,
  QUOTA_AND_BUDGET_CREATE,
  TAGGING_POLICY_CREATE
} from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import useStyles from "./BannerContent.styles";

const CONNECT_DATA_SOURCE = "connectDataSource";
const ADD_ENVIRONMENT = "addEnvironment";
const SET_POOL = "setPoolLimit";
const CLOUD_CONNECTION_BACKDROP_MESSAGE = "cloudConnectionBackdropMessage";

const redirectToCreateCloudAccount = (navigate) => navigate(CLOUD_ACCOUNT_CONNECT);
const redirectToCreateK8sAccount = (navigate) => navigate(CLOUD_ACCOUNT_CONNECT_K8S);
const openEditPoolModal = (_, poolId, { openSideModal, organizationInfo }) =>
  openSideModal(EditPoolModal, { id: poolId, info: organizationInfo });

const redirectToCreateRule = (navigate) => navigate(ASSIGNMENT_RULE_CREATE);
const redirectToCreateEnvironment = (navigate) => navigate(ENVIRONMENT_CREATE);
const redirectToCreateAnomalyDetectionPolicy = (navigate) => navigate(ANOMALY_CREATE);
const redirectToCreateQuotasAndBudgetsPolicy = (navigate) => navigate(QUOTA_AND_BUDGET_CREATE);
const redirectToCreateTaggingPolicy = (navigate) => navigate(TAGGING_POLICY_CREATE);

export const getBannerIcon = (messageType) =>
  ({
    cloudAccounts: {
      Component: DataSourceIcon,
      dataTestId: "img_connect_data_source"
    },
    dashboard: {
      Component: DataSourceIcon,
      dataTestId: "img_connect_data_source"
    },
    recommendations: {
      Component: DataSourceIcon,
      dataTestId: "img_connect_data_source"
    },
    pools: {
      Component: PoolLimitIcon,
      dataTestId: "img_set_pool_limit"
    },
    assignmentRules: {
      Component: AssignmentRuleIcon,
      dataTestId: "img_add_rule"
    },
    environments: {
      Component: EnvironmentIcon,
      dataTestId: "img_add_env"
    },
    k8sRightsizing: {
      Component: DataSourceIcon,
      dataTestId: "img_connect_data_source"
    },
    anomalyDetectionPolicy: {
      Component: DataSourceIcon,
      dataTestId: "img_add_anomaly_detection_policy"
    },
    quotasAndBudgetsPolicy: {
      Component: DataSourceIcon,
      dataTestId: "img_add_quotas_and_budget_policy"
    },
    taggingPolicy: {
      Component: DataSourceIcon,
      dataTestId: "img_add_tagging_policy"
    },
    awsCloudAccounts: {
      Component: DataSourceIcon,
      dataTestId: "img_connect_data_source"
    }
  })[messageType];

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
          subMessage: ["p_connection"]
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "dataSourcesContactManagerBackdropMessage"]
        },
        Icon: DataSourceIcon
      }
    },
    awsCloudAccounts: {
      item: {
        requiredActions: ["MANAGE_CLOUD_CREDENTIALS"],
        mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "awsDataSourcesBackdropMessage"],
        buttonMessageId: CONNECT_DATA_SOURCE,
        subMessageIds: [CLOUD_CONNECTION_BACKDROP_MESSAGE],
        onButtonClick: redirectToCreateCloudAccount,
        dataTestIds: {
          mainMessage: ["p_sample", "p_connect_ca"],
          button: "btn_connect_ca",
          wrapper: "banner_mockup",
          subMessage: ["p_connection"]
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "awsDataSourcesContactManagerBackdropMessage"]
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
          mainMessage: ["p_sample"],
          button: "btn_connect_ca",
          subMessage: ["p_connection"],
          wrapper: "banner_mockup"
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
        onButtonClick: openEditPoolModal,
        dataTestIds: {
          mainMessage: ["p_sample", "p_set_pool"],
          button: "btn_set_pool",
          wrapper: "banner_mockup"
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
          wrapper: "banner_mockup"
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
          wrapper: "banner_mockup"
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
          subMessage: ["p_connection"]
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "dataSourcesContactManagerBackdropMessage"]
        },
        Icon: DataSourceIcon
      }
    },
    anomalyDetectionPolicy: {
      item: {
        requiredActions: ["EDIT_PARTNER"],
        mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "anomalyDetectionPolicyBackdropMessage"],
        buttonMessageId: "add",
        onButtonClick: redirectToCreateAnomalyDetectionPolicy,
        dataTestIds: {
          mainMessage: ["p_sample", "p_add_anomaly_detection_policy"],
          button: "btn_add_anomaly_detection_policy",
          wrapper: "banner_mockup"
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "anomalyDetectionPolicyContactManagerBackdropMessage"]
        },
        Icon: DataSourceIcon
      }
    },
    quotasAndBudgetsPolicy: {
      item: {
        requiredActions: ["EDIT_PARTNER"],
        mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "quotasAndBudgetPolicyBackdropMessage"],
        buttonMessageId: "add",
        onButtonClick: redirectToCreateQuotasAndBudgetsPolicy,
        dataTestIds: {
          mainMessage: ["p_sample", "p_add_quotas_and_budget_policy"],
          button: "btn_add_quotas_and_budget_policy",
          wrapper: "banner_mockup"
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "quotasAndBudgetPolicyContactManagerBackdropMessage"]
        },
        Icon: DataSourceIcon
      }
    },
    taggingPolicy: {
      item: {
        requiredActions: ["EDIT_PARTNER"],
        mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "taggingPolicyBackdropMessage"],
        buttonMessageId: "add",
        onButtonClick: redirectToCreateTaggingPolicy,
        dataTestIds: {
          mainMessage: ["p_sample", "p_add_tagging_policy"],
          button: "btn_add_tagging_policy",
          wrapper: "banner_mockup",
          img: "img_add_tagging_policy"
        },
        renderIfNotAllowed: {
          mainMessageIds: ["sampleDataToGiveSenseOfTheProduct", "taggingPolicyContactManagerBackdropMessage"]
        },
        Icon: DataSourceIcon
      }
    }
  })[messageType];

const BannerContent = ({ messageType }) => {
  const { classes, cx } = useStyles();

  const { organizationPoolId, ...organizationInfo } = useOrganizationInfo();

  const navigate = useNavigate();

  const { item = {} } = getConfiguration(messageType);

  const [{ mainMessageIds = [], buttons, buttonMessageId, subMessageIds = [], onButtonClick, dataTestIds = {} } = {}] =
    useAllowedItems({
      items: [item]
    });

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

  const openSideModal = useOpenSideModal();

  return (
    <>
      {!isEmptyArray(mainMessageIds) ? renderTypography(mainMessageIds, dataTestIds.mainMessage) : null}
      {buttonMessageId && (
        <Button
          dataTestId={dataTestIds.button}
          customClass={!isEmptyArray(subMessageIds) ? classes.buttonMargin : ""}
          size="medium"
          variant="contained"
          color="success"
          onClick={() => onButtonClick(navigate, organizationPoolId, { openSideModal, organizationInfo })}
          messageId={buttonMessageId}
        />
      )}
      {Array.isArray(buttons) && (
        <div className={cx(classes.buttonsWrapper, !isEmptyArray(subMessageIds) ? classes.buttonsWrapperMargin : "")}>
          {buttons.map(({ messageId, dataTestId, onClick }) => (
            <Button
              key={messageId}
              messageId={messageId}
              customClass={classes.buttonWidth}
              onClick={() => onClick(navigate, organizationPoolId, { openSideModal, organizationInfo })}
              dataTestId={dataTestId}
              size="medium"
              variant="contained"
              color="success"
            />
          ))}
        </div>
      )}
      {!isEmptyArray(subMessageIds) && renderTypography(subMessageIds, dataTestIds.subMessage, true)}
    </>
  );
};

export default BannerContent;
