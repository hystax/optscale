import { useEffect } from "react";
import { Typography } from "@mui/material";
import { useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import SubTitle from "components/SubTitle";
import { useThemeSettingsOptions } from "hooks/useThemeSettingsOptions";
import { isMedia } from "theme";

const TypographySettingsForm = ({ variant, options, onUpdate }) => {
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
      <form onSubmit={handleSubmit(handleOnSubmit)}>
        {Object.keys(options).map((optionName) => (
          <Input
            key={optionName}
            label={optionName}
            {...register(isMedia(optionName) ? `${optionName}.fontSize` : optionName)}
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

export default TypographySettingsForm;
