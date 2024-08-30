import { useEffect } from "react";
import { Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubTitle from "components/SubTitle";
import { useThemeSettingsOptions } from "hooks/useThemeSettingsOptions";
import { OptionField } from "./FormElements";

const TypographySettingsForm = ({ variant, options, onUpdate }) => {
  const themeSettings = useThemeSettingsOptions();

  const methods = useForm({
    defaultValues: options
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...options
    }));
  }, [options, reset]);

  const handleOnSubmit = (formData) => {
    const updatedSettings = {
      ...themeSettings,
      typography: {
        ...themeSettings.typography,
        [variant]: formData
      }
    };

    onUpdate(updatedSettings);
  };

  const handleOnReset = () => {
    const updatedSettings = {
      ...themeSettings,
      typography: {
        ...themeSettings.typography,
        [variant]: {}
      }
    };

    onUpdate(updatedSettings);
  };

  return (
    <>
      <SubTitle gutterBottom>
        <FormattedMessage
          id="variantTypographySettings"
          values={{
            variant,
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />
      </SubTitle>
      <Typography gutterBottom variant={variant}>
        Lorem ipsum dolor sit amet
      </Typography>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(handleOnSubmit)}>
          {Object.keys(options).map((optionName) => (
            <OptionField key={optionName} optionName={optionName} />
          ))}
          <FormButtonsWrapper>
            <Button color="primary" messageId="save" type="submit" />
            <Button messageId="reset" onClick={handleOnReset} />
          </FormButtonsWrapper>
        </form>
      </FormProvider>
    </>
  );
};

export default TypographySettingsForm;
