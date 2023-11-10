import { useState } from "react";
import { Box, FormControlLabel, Link, Stack, Typography } from "@mui/material";
import { Controller, useForm } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import Checkbox from "components/Checkbox";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import Logo from "components/Logo";
import GenerateLiveDemoContainer from "containers/GenerateLiveDemoContainer";
import { FINOPS, HYSTAX_PRIVACY_POLICY } from "urls";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { SPACING_4 } from "utils/layouts";
import { getQueryParams } from "utils/network";
import { emailRegex } from "utils/strings";

const EMAIL = "email";
const SUBSCRIBE_TO_NEWSLETTER = "subscribeToNewsletter";

const LiveDemo = () => {
  const intl = useIntl();

  const { emailbypass } = getQueryParams(true);

  const {
    control,
    register,
    formState: { errors },
    handleSubmit
  } = useForm({
    defaultValues: {
      [EMAIL]: "",
      [SUBSCRIBE_TO_NEWSLETTER]: true
    }
  });

  const [demoParameters, setDemoParameters] = useState(null);

  // The search parameter can be of any valid type (e.g., string), so we need to explicitly check if it is equal to true.
  if (emailbypass === true) {
    return <GenerateLiveDemoContainer />;
  }

  return demoParameters ? (
    <GenerateLiveDemoContainer email={demoParameters.email} subscribeToNewsletter={demoParameters.subscribeToNewsletter} />
  ) : (
    <Stack spacing={SPACING_4} alignItems="center">
      <Box>
        <Logo width={200} dataTestId="img_logo" />
      </Box>
      <Box pl={2} pr={2}>
        <Typography align="center">
          <FormattedMessage
            id="liveDemoDisclaimer"
            values={{
              br: <br />
            }}
          />
        </Typography>
      </Box>
      <Box pl={2} pr={2}>
        <form
          noValidate
          onSubmit={handleSubmit((formData) => {
            setDemoParameters(formData);
          })}
          style={{
            maxWidth: "430px"
          }}
        >
          <Input
            label={<FormattedMessage id="email" />}
            dataTestId="input_email"
            required
            error={!!errors[EMAIL]}
            helperText={errors[EMAIL] && errors[EMAIL].message}
            {...register(EMAIL, {
              pattern: {
                value: emailRegex,
                message: intl.formatMessage({ id: "invalidEmailAddress" })
              },
              required: {
                value: true,
                message: intl.formatMessage({ id: "thisFieldIsRequired" })
              },
              maxLength: {
                value: DEFAULT_MAX_INPUT_LENGTH,
                message: intl.formatMessage(
                  { id: "maxLength" },
                  { inputName: intl.formatMessage({ id: "email" }), max: DEFAULT_MAX_INPUT_LENGTH }
                )
              }
            })}
          />
          <FormControlLabel
            control={
              <Controller
                name={SUBSCRIBE_TO_NEWSLETTER}
                control={control}
                render={({ field: { value, onChange, ...rest } }) => (
                  <Checkbox
                    data-test-id="subscribe_me_to_the_monthly_newsletter_checkbox"
                    checked={value}
                    {...rest}
                    onChange={(event) => onChange(event.target.checked)}
                  />
                )}
              />
            }
            label={
              <Typography>
                <FormattedMessage
                  id="subscribeMeToTheMonthlyNewsletter"
                  values={{
                    link: (chunks) => (
                      <Link data-test-id="link_parameters_library" href={FINOPS} target="_blank" rel="noopener">
                        {chunks}
                      </Link>
                    )
                  }}
                />
              </Typography>
            }
          />
          <FormButtonsWrapper mb={1} justifyContent="center">
            <Button
              messageId="proceedToLiveDemo"
              type="submit"
              variant="contained"
              color="primary"
              dataTestId="btn_proceed_to_live_demo"
            />
          </FormButtonsWrapper>
          <Typography variant="caption" align="center" component="div">
            <FormattedMessage
              id="agreeToHystaxPrivacyPolicy"
              values={{
                link: (chunks) => (
                  <Link data-test-id="link_privacy_policy" href={HYSTAX_PRIVACY_POLICY} target="_blank" rel="noopener">
                    {chunks}
                  </Link>
                )
              }}
            />
          </Typography>
        </form>
      </Box>
    </Stack>
  );
};

export default LiveDemo;
