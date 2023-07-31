import React, { useMemo } from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm, Controller } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Selector from "components/Selector";
import { isEmpty } from "utils/arrays";

export const NEW_DEFAULT_KEY = "newDefaultKey";

const buildSshKeysSelectorData = (keys) =>
  keys.map(({ id, name, fingerprint }) => ({
    id,
    name: `${name} (${fingerprint})`,
    value: id
  }));

const DeleteSshKeyForm = ({ onSubmit, closeSideModal, isDefaultKey, isLoading, keysToSelect = [] }) => {
  const intl = useIntl();
  const methods = useForm({
    defaultValues: {
      [NEW_DEFAULT_KEY]: ""
    }
  });

  const {
    control,
    handleSubmit,
    formState: { errors }
  } = methods;

  const selectorData = useMemo(() => ({ items: buildSshKeysSelectorData(keysToSelect) }), [keysToSelect]);
  const shouldShowSelector = !isEmpty(keysToSelect);

  const NewKeySelector = () => (
    <Controller
      name={NEW_DEFAULT_KEY}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: controllerField }) => (
        <Selector
          required
          error={!!errors[NEW_DEFAULT_KEY]}
          helperText={errors?.[NEW_DEFAULT_KEY]?.message}
          data={selectorData}
          labelId="newDefaultSshKey"
          {...controllerField}
        />
      )}
    />
  );

  const noteAboutDefaultKey = (
    <div>
      <Typography color="error" gutterBottom>
        <FormattedMessage id="youAreAboutToRemoveDefaultSsh" />
      </Typography>
    </div>
  );

  return (
    <>
      <Typography gutterBottom>
        <FormattedMessage id="removingKeyWontChange" />
      </Typography>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        {isDefaultKey && noteAboutDefaultKey}
        {isDefaultKey && shouldShowSelector && <NewKeySelector />}

        <FormButtonsWrapper>
          <ButtonLoader messageId="delete" color="error" variant="contained" type="submit" isLoading={isLoading} />
          <Button messageId="cancel" dataTestId="btn_cancel" onClick={closeSideModal} />
        </FormButtonsWrapper>
      </form>
    </>
  );
};

DeleteSshKeyForm.propTypes = {
  onSubmit: PropTypes.func,
  closeSideModal: PropTypes.func,
  isLoading: PropTypes.bool,
  isDefaultKey: PropTypes.bool,
  keysToSelect: PropTypes.array
};

export default DeleteSshKeyForm;
