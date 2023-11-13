import { useEffect } from "react";
import SquareIcon from "@mui/icons-material/Square";
import { useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import SubTitle from "components/SubTitle";
import { useThemeSettingsOptions } from "hooks/useThemeSettingsOptions";

const PaletteSettingsForm = ({ color, options, onUpdate }) => {
  const themeSettings = useThemeSettingsOptions();

  const { handleSubmit, register, reset } = useForm({
    defaultValues: options
  });

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
      <form onSubmit={handleSubmit(handleOnSubmit)}>
        {Object.entries(options).map(([optionName, optionValue]) => (
          <Input
            key={optionName}
            InputProps={{
              endAdornment: <SquareIcon style={{ border: "1px dashed black", color: optionValue }} />
            }}
            label={optionName}
            {...register(optionName)}
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
