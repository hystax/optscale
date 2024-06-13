import { Fragment, useState } from "react";
import Autocomplete from "@mui/material/Autocomplete";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { useForm, type SubmitHandler, FormProvider, useFieldArray } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import Chip from "components/Chip";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { getDifference, isEmpty as isEmptyArray } from "utils/arrays";
import { SCOPE_TYPES, EMAIL_MAX_LENGTH, MANAGER, ORGANIZATION_MANAGER } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { removeKey } from "utils/objects";
import { emailRegex, splitInvites } from "utils/strings";
import { FIELD_NAMES } from "./constants";
import { AdditionalRolesFieldArray } from "./FormElements";
import { EmailInvitations, FormValues, Invitation, InviteEmployeesFormProps } from "./types";

const ADDITIONAL_ROLES = "additionalRoles";

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

const InviteEmployeesForm = ({ availablePools, onSubmit, onCancel, isLoadingProps = {} }: InviteEmployeesFormProps) => {
  const { isCreateInvitationsLoading = false, isGetAvailablePoolsLoading = false } = isLoadingProps;

  const { name, organizationId, isDemo } = useOrganizationInfo();
  const methods = useForm<FormValues>({
    shouldUnregister: true
  });

  const { control, handleSubmit } = methods;

  const [values, setValues] = useState<{
    emails: string[];
    invalidEmails: string[];
  }>({
    emails: [],
    invalidEmails: []
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: FIELD_NAMES.ADDITIONAL_ROLES_FIELD_ARRAY.FIELD_NAME
  });

  const onSuccessCallback = () => {
    setValues({
      emails: [],
      invalidEmails: []
    });
    remove();
  };

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
      <FormProvider {...methods}>
        <form onSubmit={isDemo ? (e) => e.preventDefault() : handleSubmit(onFormSubmit)} noValidate>
          <AdditionalRolesFieldArray
            isGetAvailablePoolsLoading={isGetAvailablePoolsLoading}
            availablePools={availablePools}
            fields={fields}
            onFieldAppend={append}
            onFieldRemove={remove}
          />
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
      </FormProvider>
    </>
  );
};

export default InviteEmployeesForm;
