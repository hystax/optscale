import { useEffect } from "react";
import SquareIcon from "@mui/icons-material/Square";
import { useForm, useFieldArray } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import SubTitle from "components/SubTitle";
import { useThemeSettingsOptions } from "hooks/useThemeSettingsOptions";

const getDefaultValues = (palette, options) => ({
  [palette]: options.map((option) => ({ color: option }))
});

const PaletteSettingsForm = ({ palette, options, onUpdate }) => {
  const themeSettings = useThemeSettingsOptions();

  const { control, register, handleSubmit, reset } = useForm({
    defaultValues: getDefaultValues(palette, options)
  });

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...getDefaultValues(palette, options)
    }));
  }, [options, palette, reset]);

  const { fields } = useFieldArray({
    control,
    name: palette
  });

  const handleOnSubmit = (formData) => {
    const colors = Object.values(formData[palette]).map(({ color }) => color);

    const updatedSettings = {
      ...themeSettings,
      chartPalette: {
        ...themeSettings.chartPalette,
        [palette]: colors
      }
    };

    onUpdate(updatedSettings);
  };

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
      <form onSubmit={handleSubmit(handleOnSubmit)}>
        {fields.map((field, index) => (
          <Input
            key={field.id}
            InputProps={{
              endAdornment: <SquareIcon style={{ border: "1px dashed black", color: options[index] }} />
            }}
            label={index + 1}
            {...register(`${palette}.${index}.color`)}
          />
        ))}
        <FormButtonsWrapper>
          <Button color="primary" messageId="save" type="submit" />
          <Button messageId="reset" onClick={handleOnReset} />
        </FormButtonsWrapper>
      </form>
    </>
  );
};

export default PaletteSettingsForm;
