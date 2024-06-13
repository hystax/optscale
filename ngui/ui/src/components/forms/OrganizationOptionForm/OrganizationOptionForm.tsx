import { useState } from "react";
import FormHelperText from "@mui/material/FormHelperText";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import JsonView from "components/JsonView";
import StyledFormLabel from "components/StyledFormLabel";
import { FormButtons, OptionNameField } from "./FormElements";
import { FormValues, OrganizationOptionFormProps } from "./types";
import { getDefaultValues } from "./utils";

const OrganizationOptionForm = ({ onSubmit, onCancel, isLoading = false }: OrganizationOptionFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  const [jsonValue, setJsonValue] = useState({ key: "value" });
  const [isValidJson, setIsValidJson] = useState(true);

  const onJsonChange = ({ error, jsObject }) => {
    setJsonValue(jsObject);
    setIsValidJson(error === false);
  };

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((formData) => {
          onSubmit(formData.organizationOptionName, jsonValue);
        })}
        noValidate
      >
        <OptionNameField />
        <StyledFormLabel required>
          <FormattedMessage id="value" />
        </StyledFormLabel>
        <JsonView value={jsonValue} onChange={onJsonChange} />
        {!isValidJson && (
          <FormHelperText variant="outlined" error>
            <FormattedMessage id="optionMustBeValidJsonObject" />
          </FormHelperText>
        )}
        <FormButtons onCancel={onCancel} isLoading={isLoading} />
      </form>
    </FormProvider>
  );
};

export default OrganizationOptionForm;
