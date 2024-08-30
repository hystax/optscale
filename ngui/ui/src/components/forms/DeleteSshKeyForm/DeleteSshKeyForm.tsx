import Typography from "@mui/material/Typography";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { isEmpty } from "utils/arrays";
import { FormButtons, NewDefaultKeySelector } from "./FormElements";
import { FormValues } from "./types";
import { getDefaultValues } from "./utils";

const DeleteSshKeyForm = ({ onSubmit, closeSideModal, isDefaultKey, isLoading, keysToSelect = [] }) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  const shouldShowSelector = !isEmpty(keysToSelect);

  return (
    <>
      <Typography gutterBottom>
        <FormattedMessage id="removingKeyWontChange" />
      </Typography>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          {isDefaultKey && (
            <div>
              <Typography color="error" gutterBottom>
                <FormattedMessage id="youAreAboutToRemoveDefaultSsh" />
              </Typography>
            </div>
          )}
          {isDefaultKey && shouldShowSelector && <NewDefaultKeySelector keysToSelect={keysToSelect} />}
          <FormButtons onClose={closeSideModal} isLoading={isLoading} />
        </form>
      </FormProvider>
    </>
  );
};

export default DeleteSshKeyForm;
