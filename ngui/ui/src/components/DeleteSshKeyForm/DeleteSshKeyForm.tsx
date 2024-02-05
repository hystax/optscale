import Typography from "@mui/material/Typography";
import { useForm, Controller } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Selector, { Item, ItemContent } from "components/Selector";
import { isEmpty } from "utils/arrays";

export const NEW_DEFAULT_KEY = "newDefaultKey";

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
          id="ssh-key-selector"
          required
          error={!!errors[NEW_DEFAULT_KEY]}
          helperText={errors?.[NEW_DEFAULT_KEY]?.message}
          labelMessageId="newDefaultSshKey"
          {...controllerField}
        >
          {keysToSelect.map(({ id, name, fingerprint }) => (
            <Item key={id} value={id}>
              <ItemContent>{`${name} (${fingerprint})`}</ItemContent>
            </Item>
          ))}
        </Selector>
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

export default DeleteSshKeyForm;
