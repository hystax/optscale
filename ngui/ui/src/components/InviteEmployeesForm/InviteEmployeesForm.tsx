import { Fragment, useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box } from "@mui/material";
import Autocomplete from "@mui/material/Autocomplete";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { useForm, useFieldArray, Controller, type SubmitHandler, type FieldError } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import Chip from "components/Chip";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import IconButton from "components/IconButton";
import Input from "components/Input";
import Selector, { Item, ItemContent, ItemContentWithPoolIcon } from "components/Selector";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { getDifference, isEmpty as isEmptyArray } from "utils/arrays";
import {
  SCOPE_TYPES,
  EMAIL_MAX_LENGTH,
  MANAGER,
  ENGINEER,
  ORGANIZATION_MANAGER,
  POOL_TYPES,
  INVITABLE_ROLE_PURPOSES
} from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { removeKey } from "utils/objects";
import { emailRegex, splitInvites } from "utils/strings";
import useStyles from "./InviteEmployeesForm.styles";

const ADDITIONAL_ROLES = "additionalRoles";
const ROLE = "role";
const POOL_ID = "poolId";
const DEFAULT_ADDITIONAL_ROLE_CONDITION = { role: "", poolId: "" } as const;

type Pool = {
  id: string;
  name: string;
  parent_id: string | null;
  pool_purpose: keyof typeof POOL_TYPES;
};

type PoolTreeNode = Pool & {
  level: number;
  children: PoolTreeNode[];
};

type Invitation = { scope_id: string; scope_type: (typeof SCOPE_TYPES)[keyof typeof SCOPE_TYPES]; purpose: string | null };

type EmailInvitations = Record<string, Invitation[]>;

type InviteEmployeesFormProps = {
  availablePools: Pool[];
  onSubmit: (invitations: EmailInvitations, successCallback: () => void) => void;
  onCancel: () => void;
  isLoadingProps?: {
    isCreateInvitationsLoading?: boolean;
    isGetAvailablePoolsLoading?: boolean;
  };
};

type FormValues = {
  additionalRoles: { role: keyof typeof INVITABLE_ROLE_PURPOSES; poolId: string }[];
};

const getEmailInvitations = (
  additionalRoles: FormValues["additionalRoles"],
  organizationId: string,
  emails: string[]
): EmailInvitations => {
  const invitations: Invitation[] = !isEmptyArray(additionalRoles)
    ? additionalRoles.map((item) => ({
        scope_id: item.role === ORGANIZATION_MANAGER ? organizationId : item.poolId,
        scope_type: item.role === ORGANIZATION_MANAGER ? SCOPE_TYPES.ORGANIZATION : SCOPE_TYPES.POOL,
        purpose: item.role === ORGANIZATION_MANAGER ? MANAGER : item.role
      }))
    : [{ scope_id: organizationId, scope_type: SCOPE_TYPES.ORGANIZATION, purpose: null }];

  return Object.fromEntries(emails.map((email) => [email, invitations]));
};

const flattenPoolTree = (poolsTree: PoolTreeNode[], level = 0): PoolTreeNode[] =>
  poolsTree.flatMap((pool) => [pool, ...flattenPoolTree(pool.children, level + 1)]);

const getPoolTree = (pools: InviteEmployeesFormProps["availablePools"], id: string | null = null, level = 0): PoolTreeNode[] =>
  [...pools]
    .sort((a, b) => a.name.localeCompare(b.name))
    .filter((pool) => pool.parent_id === id)
    .map((pool) => ({
      ...pool,
      level,
      children: getPoolTree(pools, pool.id, level + 1)
    }));

const InviteEmployeesForm = ({ availablePools, onSubmit, onCancel, isLoadingProps = {} }: InviteEmployeesFormProps) => {
  const { classes, cx } = useStyles();

  const flatPools = flattenPoolTree(getPoolTree(availablePools));
  const { isCreateInvitationsLoading = false, isGetAvailablePoolsLoading = false } = isLoadingProps;

  const { name, organizationId, isDemo } = useOrganizationInfo();
  const {
    control,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm<FormValues>({
    shouldUnregister: true
  });

  const [values, setValues] = useState<{
    emails: string[];
    invalidEmails: string[];
  }>({
    emails: [],
    invalidEmails: []
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: ADDITIONAL_ROLES
  });

  const onSuccessCallback = () => {
    setValues({
      emails: [],
      invalidEmails: []
    });
    remove();
  };

  const watchAdditionalRoles = watch(ADDITIONAL_ROLES);
  const busyPoolIds = watchAdditionalRoles?.map((item) => item[POOL_ID]) ?? [];
  const busyRoles = watchAdditionalRoles?.map((item) => item[ROLE]) ?? [];

  const [isEmptyEmail, setIsEmptyEmail] = useState(false);
  const [isOnlyInvalidEmail, setIsOnlyInvalidEmail] = useState(false);

  const onFormSubmit: SubmitHandler<FormValues> = (formData) => {
    const { emails, invalidEmails } = values;
    if (isEmptyArray(emails)) {
      // Custom error handling for email field, since it is not a part of the form
      // TODO - onFormSubmit will not be triggered if there are validation error on the form itself, the error will not be shown
      // investigate if it is possible to make autocomplete a form field
      if (isEmptyArray(invalidEmails)) {
        return setIsEmptyEmail(true);
      }
      return setIsOnlyInvalidEmail(true);
    }

    return onSubmit(getEmailInvitations(formData[ADDITIONAL_ROLES], organizationId, emails), onSuccessCallback);
  };

  const organizationMemberRow = (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={4}>
        <Input
          InputProps={{
            readOnly: true
          }}
          defaultValue={intl.formatMessage({ id: "member" })}
          label={<FormattedMessage id="role" />}
          type="text"
          dataTestId="input_role"
        />
      </Grid>
      <Grid item xs={8}>
        <Input
          InputProps={{
            readOnly: true
          }}
          defaultValue={name}
          label={<FormattedMessage id="organization" />}
          type="text"
          dataTestId="input_org"
        />
      </Grid>
    </Grid>
  );

  const renderOrganizationField = (count: number) => (
    <Input
      required
      InputProps={{
        readOnly: true
      }}
      defaultValue={name}
      label={<FormattedMessage id="organization" />}
      type="text"
      dataTestId={`input_org_${count}`}
    />
  );

  const renderPoolField = (count: number, error?: FieldError) => (
    <Controller
      name={`${ADDITIONAL_ROLES}.${count}.${POOL_ID}`}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field }) => (
        <Selector
          id="pool-selector"
          labelMessageId="pool"
          required
          error={!!error}
          fullWidth
          helperText={error && error.message}
          isLoading={isGetAvailablePoolsLoading}
          {...field}
        >
          {flatPools.map((obj) => (
            <Item
              key={obj.id}
              value={obj.id}
              depth={obj.level}
              disabled={busyPoolIds.includes(obj.id) && obj.id !== field.value}
            >
              <Box>
                <ItemContentWithPoolIcon poolType={obj.pool_purpose}>{obj.name}</ItemContentWithPoolIcon>
              </Box>
            </Item>
          ))}
        </Selector>
      )}
    />
  );

  const additionalRolesRow = (count: number) => {
    const roleError = errors?.[ADDITIONAL_ROLES]?.[count]?.[ROLE];
    const poolError = errors?.[ADDITIONAL_ROLES]?.[count]?.[POOL_ID];

    const additionalRole = watchAdditionalRoles?.[count]?.[ROLE];

    const getScopeFieldRenderer = () => {
      const poolFieldRenderer = () => renderPoolField(count, poolError);
      const organizationFieldRender = () => renderOrganizationField(count);
      return (
        {
          [ORGANIZATION_MANAGER]: organizationFieldRender,
          [MANAGER]: poolFieldRenderer,
          [ENGINEER]: poolFieldRenderer
        }[additionalRole] || poolFieldRenderer
      );
    };

    const renderScopeField = getScopeFieldRenderer();

    return (
      <Grid container spacing={SPACING_1}>
        <Grid item xs={4}>
          <Box>
            <Controller
              name={`${ADDITIONAL_ROLES}.${count}.${ROLE}`}
              control={control}
              rules={{
                required: {
                  value: true,
                  message: intl.formatMessage({ id: "thisFieldIsRequired" })
                }
              }}
              render={({ field }) => (
                <Selector
                  id="role-selector"
                  labelMessageId="role"
                  required
                  error={!!roleError}
                  helperText={roleError && roleError.message}
                  fullWidth
                  {...field}
                >
                  {Object.entries(INVITABLE_ROLE_PURPOSES).map(([role, roleMessageId]) => (
                    <Item
                      key={role}
                      value={role}
                      disabled={
                        role === ORGANIZATION_MANAGER && busyRoles.includes(ORGANIZATION_MANAGER) && role !== field.value
                      }
                    >
                      <ItemContent>
                        <FormattedMessage id={roleMessageId} />
                      </ItemContent>
                    </Item>
                  ))}
                </Selector>
              )}
            />
          </Box>
        </Grid>
        <Grid item xs={8}>
          <Box display="flex">
            <Box flexGrow={1}>{renderScopeField()}</Box>
            <Box>
              <FormControl className={cx(classes.item, classes.deleteButton)}>
                <IconButton
                  color="error"
                  icon={<DeleteOutlinedIcon />}
                  onClick={() => remove(count)}
                  tooltip={{
                    show: true,
                    value: <FormattedMessage id="delete" />
                  }}
                  dataTestId={`btn_delete_${count}`}
                />
              </FormControl>
            </Box>
          </Box>
        </Grid>
      </Grid>
    );
  };

  const isEmailValid = (email: string) => emailRegex.test(email) && email.length <= EMAIL_MAX_LENGTH;

  const saveEmails = (emails: string[]) => {
    emails.forEach((email) => {
      if (isEmailValid(email)) {
        setValues((prevState) => ({ ...prevState, emails: [...new Set([...prevState.emails, email])] }));
      } else {
        setValues((prevState) => ({ ...prevState, invalidEmails: [...new Set([...prevState.invalidEmails, email])] }));
      }
      // Clear error state for email field
      setIsEmptyEmail(false);
      setIsOnlyInvalidEmail(false);
    });
  };

  const emailsChange = (emailsString: string) => saveEmails(splitInvites(emailsString));

  const handleEmailsChange = (email: string) => {
    emailsChange(email);
  };

  const deleteEmail = (option: string) => {
    const { emails, invalidEmails } = values;
    if (emails.includes(option)) {
      setValues({
        ...values,
        emails: emails.filter((email) => email !== option)
      });
    } else {
      setValues({
        ...values,
        invalidEmails: invalidEmails.filter((email) => email !== option)
      });
    }
  };

  const getEmailValidation = () => {
    if (isEmptyEmail) {
      return intl.formatMessage({ id: "thisFieldIsRequired" });
    }
    if (isOnlyInvalidEmail) {
      return intl.formatMessage({ id: "notContainAnyValidEmails" });
    }
    return null;
  };

  return (
    <>
      <Typography paragraph data-test-id="p_enter_employees">
        <FormattedMessage id="inviteUsersInviteEnterEmail" />
      </Typography>
      <Autocomplete
        multiple
        freeSolo
        disableClearable
        options={[]}
        clearOnBlur
        value={values.emails.concat(values.invalidEmails)}
        onChange={(event, value, reason) => {
          if (reason === "removeOption") {
            let diff = getDifference(values.emails, value);
            let [first] = diff;
            if (first) {
              return deleteEmail(first);
            }
            diff = getDifference(values.invalidEmails, value);
            [first] = diff;
            if (first) {
              return deleteEmail(first);
            }
          }
          const email = event.target.value;
          return handleEmailsChange(email);
        }}
        onClose={(event, reason) => {
          if (reason === "blur") {
            const email = event.target.value;
            if (email) {
              return handleEmailsChange(email);
            }
          }
          return null;
        }}
        renderTags={(value, getTagProps) =>
          value.map((option, index) => (
            <Chip
              onDelete={() => deleteEmail(option)}
              key={option}
              size="small"
              label={<span data-test-id={`chip_email_${index}`}>{option}</span>}
              color={values.invalidEmails.includes(option) ? "error" : "info"}
              dataTestIds={{
                chip: `chip_${index}`,
                deleteIcon: `chip_btn_close_${index}`
              }}
              {...removeKey(getTagProps({ index }), "onDelete")}
            />
          ))
        }
        renderInput={(params) => (
          <Input
            {...params}
            dataTestId="input_email"
            error={isEmptyEmail || isOnlyInvalidEmail}
            helperText={getEmailValidation()}
            label={<FormattedMessage id="email" />}
            required
          />
        )}
      />
      {organizationMemberRow}
      <form onSubmit={isDemo ? (e) => e.preventDefault() : handleSubmit(onFormSubmit)} noValidate>
        {fields.map((item, index) => (
          <Fragment key={item.id}>{additionalRolesRow(index)}</Fragment>
        ))}
        <FormControl fullWidth>
          <Button
            dashedBorder
            startIcon={<AddOutlinedIcon />}
            messageId="addRole"
            dataTestId="btn_add"
            size="large"
            color="primary"
            onClick={() => append(DEFAULT_ADDITIONAL_ROLE_CONDITION)}
          />
        </FormControl>
        <FormButtonsWrapper>
          <ButtonLoader
            messageId="invite"
            dataTestId="btn_invite"
            color="primary"
            variant="contained"
            type="submit"
            disabled={isDemo}
            tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
            isLoading={isCreateInvitationsLoading || isGetAvailablePoolsLoading}
          />
          <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
        </FormButtonsWrapper>
      </form>
    </>
  );
};

export default InviteEmployeesForm;
