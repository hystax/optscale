import { useEffect } from "react";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubTitle from "components/SubTitle";
import { useThemeSettingsOptions } from "hooks/useThemeSettingsOptions";
import { ColorsFieldArray } from "./FormElements";
import { getDefaultValues } from "./utils";

const PaletteSettingsForm = ({ palette, options, onUpdate }) => {
  const themeSettings = useThemeSettingsOptions();

  const methods = useForm({
    defaultValues: getDefaultValues(palette, options)
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...getDefaultValues(palette, options)
    }));
  }, [options, palette, reset]);

  const handleOnSubmit = handleSubmit((formData) => {
    const colors = Object.values(formData[palette]).map(({ color }) => color);
    const updatedSettings = {
      ...themeSettings,
      chartPalette: {
        ...themeSettings.chartPalette,
        [palette]: colors
      }
    };
    onUpdate(updatedSettings);
  });

  const handleOnReset = () => {
    const updatedSettings = {
      ...themeSettings,
      chartPalette: {
        ...themeSettings.chartPalette,
        [palette]: []
      }
    };

    onUpdate(updatedSettings);
  };

  return (
    <>
      <SubTitle gutterBottom>
        <FormattedMessage
          id="chartPaletteSettings"
          values={{
            palette,
            strong: (chunks) => <strong>{chunks}</strong>
          }}
        />
      </SubTitle>
      <FormProvider {...methods}>
        <form onSubmit={handleOnSubmit}>
          <ColorsFieldArray fieldName={palette} options={options} />
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
