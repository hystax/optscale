import { useEffect } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubTitle from "components/SubTitle";
import { useThemeSettingsOptions } from "hooks/useThemeSettingsOptions";
import { OptionField } from "./FormElements";

const PaletteSettingsForm = ({ color, options, onUpdate }) => {
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
      palette: {
        ...themeSettings.palette,
        [color]: formData
      }
    };

    onUpdate(updatedSettings);
  };

  const handleOnReset = () => {
    const updatedSettings = {
      ...themeSettings,
      palette: {
        ...themeSettings.palette,
        [color]: {}
      }
    };

    onUpdate(updatedSettings);
  };

  return (
    <>
      <SubTitle gutterBottom>
        <FormattedMessage
          id="colorPaletteSettings"
          values={{
            color,
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />
      </SubTitle>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(handleOnSubmit)}>
          {Object.entries(options).map(([optionName, optionValue]) => (
            <OptionField key={optionName} optionName={optionName} optionValue={optionValue} />
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

export default PaletteSettingsForm;
