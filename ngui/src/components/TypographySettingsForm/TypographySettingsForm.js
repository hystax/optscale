import React, { useEffect } from "react";
import { Typography } from "@mui/material";
import PropTypes from "prop-types";
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
  const { handleSubmit, register, reset, getValues } = useForm({
    defaultValues: options
  });

  useEffect(() => {
    reset({
      ...getValues(),
      ...options
    });
  }, [getValues, options, reset]);

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

TypographySettingsForm.propTypes = {
  variant: PropTypes.oneOf(["body1", "body2", "subtitle1", "subtitle2", "h1", "h2", "h3", "h4", "h5", "h6"]).isRequired,
  options: PropTypes.object.isRequired,
  onUpdate: PropTypes.func.isRequired
};

export default TypographySettingsForm;
