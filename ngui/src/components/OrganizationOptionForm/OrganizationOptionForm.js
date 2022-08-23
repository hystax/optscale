import React, { useState } from "react";
import FormHelperText from "@mui/material/FormHelperText";
import PropTypes from "prop-types";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import JsonView from "components/JsonView";
import StyledFormLabel from "components/StyledFormLabel";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import OrganizationOptionNameInput from "./Fields/OrganizationOptionNameInput";

const ORGANIZATION_OPTION_NAME_INPUT_NAME = "organizationOptionName";

const OrganizationOptionForm = ({ onSubmit, onCancel, isLoading = false }) => {
  const methods = useForm();
  const { handleSubmit } = methods;

  const [jsonValue, setJsonValue] = useState({});
  const [isValidJson, setIsValidJson] = useState(true);

  const onJsonChange = ({ error, jsObject }) => {
    setJsonValue(jsObject);
    setIsValidJson(error === false);
  };

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((formData) => {
          onSubmit(formData[ORGANIZATION_OPTION_NAME_INPUT_NAME], jsonValue);
        })}
        noValidate
      >
        <OrganizationOptionNameInput name={ORGANIZATION_OPTION_NAME_INPUT_NAME} />
        <StyledFormLabel required>
          <FormattedMessage id="value" />
        </StyledFormLabel>
        <JsonView value={jsonValue} onChange={onJsonChange} />
        {!isValidJson && (
          <FormHelperText variant="outlined" error>
            <FormattedMessage id="optionMustBeValidJsonObject" />
          </FormHelperText>
        )}
        <FormButtonsWrapper>
          <SubmitButtonLoader
            messageId="create"
            isLoading={isLoading}
            dataTestId="btn_create_organization_option"
            loaderDataTestId="btn_create_organization_option_loader"
          />
          <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

OrganizationOptionForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default OrganizationOptionForm;
