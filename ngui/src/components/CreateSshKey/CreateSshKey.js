import React from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import CreateSshKeyNameField, { KEY_NAME_FIELD_ID } from "components/CreateSshKeyNameField";
import CreateSshKeyValueField, { KEY_VALUE_FIELD_ID } from "components/CreateSshKeyValueField";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { SPACING_4 } from "utils/layouts";

const CreateSshKey = ({ onSubmit, isSubmitLoading = false }) => {
  const methods = useForm({
    defaultValues: {
      [KEY_NAME_FIELD_ID]: "",
      [KEY_VALUE_FIELD_ID]: ""
    }
  });

  return (
    <Grid container spacing={SPACING_4}>
      <Grid item xs={12}>
        <Typography data-test-id="ssh-hint">
          <FormattedMessage id={"sshHint"} />
        </Typography>
      </Grid>
      <Grid item>
        <FormProvider {...methods}>
          <form
            onSubmit={methods.handleSubmit((data) => {
              onSubmit(data);
              methods.reset(); // TODO: reset only on success
            })}
            noValidate
          >
            <CreateSshKeyNameField />
            <CreateSshKeyValueField />
            <FormButtonsWrapper>
              <SubmitButtonLoader
                messageId="add"
                isLoading={isSubmitLoading}
                dataTestId="btn_create_key"
                loaderDataTestId="btn_create_key_loader"
              />
            </FormButtonsWrapper>
          </form>
        </FormProvider>
      </Grid>
    </Grid>
  );
};

CreateSshKey.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isSubmitLoading: PropTypes.bool
};

export default CreateSshKey;
