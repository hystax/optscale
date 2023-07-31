import React, { Fragment, useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import Autocomplete from "@mui/material/Autocomplete";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm, useFieldArray, Controller } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import Chip from "components/Chip";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import IconButton from "components/IconButton";
import Input from "components/Input";
import PoolTypeIcon from "components/PoolTypeIcon";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { getDifference, isEmpty } from "utils/arrays";
import { SCOPE_TYPES, EMAIL_MAX_LENGTH, MANAGER, ROLE_PURPOSES, ENGINEER, ORGANIZATION_MANAGER } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { removeKey } from "utils/objects";
import { emailRegex, splitInvites } from "utils/strings";
import useStyles from "./InviteEmployeesForm.styles";

const ADDITIONAL_ROLES = "additionalRoles";
const ROLE = "role";
const POOL_ID = "poolId";
const DEFAULT_ADDITIONAL_ROLE_CONDITION = { role: "", poolId: "" };

const buildRolesSelectorData = (roles, selected, busyRoles) => ({
  selected,
  items: roles.map((role) => ({
    value: role,
    name: <FormattedMessage id={ROLE_PURPOSES[role]} />,
    disabled: role === ORGANIZATION_MANAGER && busyRoles.includes(ORGANIZATION_MANAGER) && role !== selected
  }))
});

const buildPoolsSelectorData = (selected, data, busyPoolIds) => ({
  selected,
  items: data.map((obj) => ({
    name: obj.name,
    value: obj.id,
    type: obj.pool_purpose,
    disabled: busyPoolIds.includes(obj.id) && obj.id !== selected
  }))
});

const getFormattedData = (additionalRoles, organizationId, emails) =>
  emails.reduce(
    (invitations, email) => ({
      ...invitations,
      [email]: !isEmpty(additionalRoles)
        ? additionalRoles.map((item) => ({
            scope_id: item.role === ORGANIZATION_MANAGER ? organizationId : item.poolId,
            scope_type: item.role === ORGANIZATION_MANAGER ? SCOPE_TYPES.ORGANIZATION : SCOPE_TYPES.POOL,
            purpose: item.role === ORGANIZATION_MANAGER ? MANAGER : item.role
          }))
        : [{ scope_id: organizationId, scope_type: SCOPE_TYPES.ORGANIZATION, purpose: null }]
    }),
    {}
  );

const InviteEmployeesForm = ({ availablePools, onSubmit, onCancel, isLoadingProps = {} }) => {
  const { classes, cx } = useStyles();

  const { isCreateInvitationsLoading = false, isGetAvailablePoolsLoading = false } = isLoadingProps;

  const { name, organizationId, isDemo } = useOrganizationInfo();
  const {
    control,
    handleSubmit,
    watch,
    formState: { errors }
  } = useForm({
    shouldUnregister: true
  });

  const [values, setValues] = useState({
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

  const onFormSubmit = (formData) => {
    const { emails, invalidEmails } = values;
    if (isEmpty(emails)) {
      // Custom error handling for email field, since it is not a part of the form
      // TODO - onFormSubmit will not be triggered if there are validation error on the form itself, the error will not be shown
      // investigate if it is possible to make autocomplete a form field
      if (isEmpty(invalidEmails)) {
        return setIsEmptyEmail(true);
      }
      return setIsOnlyInvalidEmail(true);
    }
    return onSubmit(getFormattedData(formData[ADDITIONAL_ROLES], organizationId, emails), onSuccessCallback);
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

  const renderOrganizationField = (count) => (
    <Grid item xs={7}>
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
    </Grid>
  );

  const renderPoolField = (count, error) => (
    <Grid item xs={7}>
      {isGetAvailablePoolsLoading ? (
        <SelectorLoader readOnly fullWidth labelId="pool" isRequired />
      ) : (
        <Controller
          name={`${ADDITIONAL_ROLES}.${count}.${POOL_ID}`}
          control={control}
          rules={{
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            }
          }}
          render={({ field: { onChange, value } }) => (
            <Selector
              data={buildPoolsSelectorData(value, availablePools, busyPoolIds)}
              menuItemIcon={{
                component: PoolTypeIcon,
                getComponentProps: (itemInfo) => ({
                  type: itemInfo.type
                })
              }}
              labelId="pool"
              dataTestId={`selector_pool_${count}`}
              required
              onChange={(selected) => onChange(selected)}
              error={!!error}
              helperText={error && error.message}
              customClass={classes.item}
            />
          )}
        />
      )}
    </Grid>
  );

  const additionalRolesRow = (count) => {
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
          <Controller
            name={`${ADDITIONAL_ROLES}.${count}.${ROLE}`}
            control={control}
            rules={{
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              }
            }}
            render={({ field: { onChange, value } }) => (
              <Selector
                data={buildRolesSelectorData([ORGANIZATION_MANAGER, MANAGER, ENGINEER], value, busyRoles)}
                labelId="role"
                dataTestId={`selector_role_${count}`}
                required
                onChange={(selected) => onChange(selected)}
                error={!!roleError}
                helperText={roleError && roleError.message}
                customClass={classes.item}
              />
            )}
          />
        </Grid>
        {renderScopeField()}
        <Grid item xs={1}>
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
        </Grid>
      </Grid>
    );
  };

  const isEmailValid = (email) => emailRegex.test(email) && email.length <= EMAIL_MAX_LENGTH;

  const saveEmails = (emails) => {
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

  const emailsChange = (emailsString) => saveEmails(splitInvites(emailsString));

  const handleEmailsChange = (email) => {
    emailsChange(email);
  };

  const deleteEmail = (option) => {
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

InviteEmployeesForm.propTypes = {
  availablePools: PropTypes.array.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoadingProps: PropTypes.shape({
    isGetAvailablePoolsLoading: PropTypes.bool,
    isCreateInvitationsLoading: PropTypes.bool
  })
};

export default InviteEmployeesForm;
