import { Box, CircularProgress, Stack, Switch, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Accordion from "components/Accordion";
import Chip from "components/Chip";
import KeyValueLabel from "components/KeyValueLabel";
import PanelLoader from "components/PanelLoader";
import SubTitle from "components/SubTitle";
import { useUpdateEmployeeEmailMutation, useUpdateEmployeeEmailsMutation } from "graphql/__generated__/hooks/restapi";
import { isEmptyArray } from "utils/arrays";
import { SPACING_2 } from "utils/layouts";
import { ObjectKeys } from "utils/types";
import {
  ApiEmployeeEmail,
  EmailSettingProps,
  EmployeeEmail,
  LoadingSwitchProps,
  UserEmailNotificationSettingsProps,
  UserEmailSettingsProps,
} from "./types";

const EMAIL_TEMPLATES = {
  finOps: {
    weekly_expense_report: {
      title: "emailTemplates.finOps.weekly_expense_report.title",
      description: "emailTemplates.finOps.weekly_expense_report.description",
    },
    pool_exceed_resources_report: {
      title: "emailTemplates.finOps.pool_exceed_resources_report.title",
      description: "emailTemplates.finOps.pool_exceed_resources_report.description",
    },
    pool_exceed_report: {
      title: "emailTemplates.finOps.pool_exceed_report.title",
      description: "emailTemplates.finOps.pool_exceed_report.description",
    },
    alert: {
      title: "emailTemplates.finOps.alert.title",
      description: "emailTemplates.finOps.alert.description",
    },
    saving_spike: {
      title: "emailTemplates.finOps.saving_spike.title",
      description: "emailTemplates.finOps.saving_spike.description",
    },
  },
  policy: {
    resource_owner_violation_report: {
      title: "emailTemplates.policy.resource_owner_violation_report.title",
      description: "emailTemplates.policy.resource_owner_violation_report.description",
    },
    pool_owner_violation_report: {
      title: "emailTemplates.policy.pool_owner_violation_report.title",
      description: "emailTemplates.policy.pool_owner_violation_report.description",
    },
    resource_owner_violation_alert: {
      title: "emailTemplates.policy.resource_owner_violation_alert.title",
      description: "emailTemplates.policy.resource_owner_violation_alert.description",
    },
    anomaly_detection_alert: {
      title: "emailTemplates.policy.anomaly_detection_alert.title",
      description: "emailTemplates.policy.anomaly_detection_alert.description",
    },
    organization_policy_expiring_budget: {
      title: "emailTemplates.policy.organization_policy_expiring_budget.title",
      description: "emailTemplates.policy.organization_policy_expiring_budget.description",
    },
    organization_policy_quota: {
      title: "emailTemplates.policy.organization_policy_quota.title",
      description: "emailTemplates.policy.organization_policy_quota.description",
    },
    organization_policy_recurring_budget: {
      title: "emailTemplates.policy.organization_policy_recurring_budget.title",
      description: "emailTemplates.policy.organization_policy_recurring_budget.description",
    },
    organization_policy_tagging: {
      title: "emailTemplates.policy.organization_policy_tagging.title",
      description: "emailTemplates.policy.organization_policy_tagging.description",
    },
  },
  recommendations: {
    new_security_recommendation: {
      title: "emailTemplates.recommendations.new_security_recommendation.title",
      description: "emailTemplates.recommendations.new_security_recommendation.description",
    },
  },
  systemNotifications: {
    environment_changes: {
      title: "emailTemplates.systemNotifications.environment_changes.title",
      description: "emailTemplates.systemNotifications.environment_changes.description",
    },
    report_imports_passed_for_org: {
      title: "emailTemplates.systemNotifications.report_imports_passed_for_org.title",
      description: "emailTemplates.systemNotifications.report_imports_passed_for_org.description",
    },
    report_import_failed: {
      title: "emailTemplates.systemNotifications.report_import_failed.title",
      description: "emailTemplates.systemNotifications.report_import_failed.description",
    },
  },
  accountManagement: {
    invite: {
      title: "emailTemplates.accountManagement.invite.title",
      description: "emailTemplates.accountManagement.invite.description",
    },
  },
} as const;

const LoadingSwitch = ({ checked, onChange, isLoading = false }: LoadingSwitchProps) => {
  const icon = (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: 20,
        height: 20,
        borderRadius: "50%",
        backgroundColor: (theme) => (checked ? theme.palette.secondary.main : theme.palette.background.default),
        boxShadow: (theme) => theme.shadows[1],
      }}
    >
      {isLoading && <CircularProgress size={14} thickness={6} />}
    </Box>
  );

  return <Switch checked={checked} onChange={onChange} icon={icon} checkedIcon={icon} disabled={isLoading} />;
};

const EmailSetting = ({ emailId, employeeId, enabled, emailTitle, description }: EmailSettingProps) => {
  const [updateEmployeeEmail, { loading: updateEmployeeEmailLoading }] = useUpdateEmployeeEmailMutation();

  return (
    <Box>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box>
          <FormattedMessage id={emailTitle} />
        </Box>
        <LoadingSwitch
          checked={enabled}
          onChange={(event) => {
            const { checked } = event.target;

            updateEmployeeEmail({
              variables: {
                employeeId,
                params: {
                  emailId,
                  action: checked ? "enable" : "disable",
                },
              },
            });
          }}
          isLoading={updateEmployeeEmailLoading}
        />
      </Box>
      <Typography variant="caption">
        <FormattedMessage id={description} />
      </Typography>
    </Box>
  );
};

const UserEmailSettings = ({ title, employeeEmails }: UserEmailSettingsProps) => {
  const { employee_id: employeeId } = employeeEmails[0];

  const [updateEmployeeEmails, { loading: updateEmployeeEmailsLoading }] = useUpdateEmployeeEmailsMutation();

  const areAllEmailsEnabled = employeeEmails.every((email) => email.enabled);

  const enabledEmailsCount = employeeEmails.filter((email) => email.enabled).length;
  const totalEmailsCount = employeeEmails.length;

  return (
    <Accordion
      headerDataTestId={`lbl_${title}_title`}
      disableExpandedSpacing
      enabledBorder
      expandTitleColor="background"
      alwaysHighlightTitle
      disableShadows
      sx={{
        maxWidth: "650px",
        // add padding to align the title switch with the switches in the accordion details
        "& .MuiAccordionSummary-root": {
          paddingRight: (theme) => theme.spacing(2),
        },
      }}
    >
      <Box display="flex" alignItems="center" rowGap={0.5} width="100%" justifyContent="space-between">
        <Box display="flex" alignItems="center" flexWrap="wrap" columnGap={1} rowGap={0.5}>
          <SubTitle variant="body2">{title}</SubTitle>
          <Chip
            multiline
            variant="outlined"
            label={
              <KeyValueLabel
                keyMessageId="active"
                isBoldValue={false}
                value={
                  <FormattedMessage
                    id="value/value"
                    values={{
                      value1: enabledEmailsCount,
                      value2: totalEmailsCount,
                    }}
                  />
                }
              />
            }
          />
        </Box>
        <Box
          onClick={(e) => {
            // prevent opening the accordion when clicking on the switch
            e.stopPropagation();
          }}
        >
          <LoadingSwitch
            checked={areAllEmailsEnabled}
            onChange={(event) => {
              const { checked } = event.target;

              updateEmployeeEmails({
                variables: {
                  employeeId,
                  params: {
                    [checked ? "enable" : "disable"]: employeeEmails.map((email) => email.id),
                  },
                },
              });
            }}
            isLoading={updateEmployeeEmailsLoading}
          />
        </Box>
      </Box>
      <Stack spacing={SPACING_2}>
        {employeeEmails.map((email) => {
          const { id: emailId, enabled, title: emailTitle, description } = email;

          return (
            <EmailSetting
              key={emailId}
              emailId={emailId}
              employeeId={employeeId}
              enabled={enabled}
              emailTitle={emailTitle}
              description={description}
            />
          );
        })}
      </Stack>
    </Accordion>
  );
};

const getGroupedEmailTemplates = (employeeEmails: ApiEmployeeEmail[]) => {
  const employeeEmailsMap = Object.fromEntries(employeeEmails.map((email) => [email.email_template, email]));

  return Object.fromEntries(
    Object.entries(EMAIL_TEMPLATES).map(([groupName, templates]) => [
      groupName,
      Object.entries(templates)
        .filter(([templateName]) => templateName in employeeEmailsMap)
        .map(([templateName, { title, description }]) => {
          const email = employeeEmailsMap[templateName];

          return { ...email, title, description } as EmployeeEmail;
        })
        .filter(({ available_by_role: availableByRole }) => availableByRole),
    ])
  ) as {
    [K in ObjectKeys<typeof EMAIL_TEMPLATES>]: EmployeeEmail[];
  };
};

const UserEmailNotificationSettings = ({ employeeEmails, isLoading = false }: UserEmailNotificationSettingsProps) => {
  if (isLoading) {
    return <PanelLoader />;
  }

  if (isEmptyArray(employeeEmails)) {
    return <FormattedMessage id="noAvailableEmailNotifications" />;
  }

  const { finOps, policy, recommendations, systemNotifications, accountManagement } = getGroupedEmailTemplates(employeeEmails);
  return (
    <>
      {isEmptyArray(finOps) ? null : <UserEmailSettings title={<FormattedMessage id="finops" />} employeeEmails={finOps} />}
      {isEmptyArray(policy) ? null : (
        <UserEmailSettings title={<FormattedMessage id="policyAlertsTitle" />} employeeEmails={policy} />
      )}
      {isEmptyArray(recommendations) ? null : (
        <UserEmailSettings title={<FormattedMessage id="recommendations" />} employeeEmails={recommendations} />
      )}
      {isEmptyArray(systemNotifications) ? null : (
        <UserEmailSettings title={<FormattedMessage id="systemNotificationsTitle" />} employeeEmails={systemNotifications} />
      )}
      {isEmptyArray(accountManagement) ? null : (
        <UserEmailSettings title={<FormattedMessage id="accountManagementTitle" />} employeeEmails={accountManagement} />
      )}
    </>
  );
};

export default UserEmailNotificationSettings;
