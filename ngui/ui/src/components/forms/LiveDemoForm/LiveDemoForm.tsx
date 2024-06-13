import { Link, Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { HYSTAX_PRIVACY_POLICY } from "urls";
import { EmailField, SubscribeToNewsletterCheckbox } from "./FormElements";
import { FormValues, LiveDemoFormProps } from "./types";
import { getDefaultValues } from "./utils";

const LiveDemoForm = ({ onSubmit }: LiveDemoFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        noValidate
        onSubmit={handleSubmit(onSubmit)}
        style={{
          maxWidth: "430px"
        }}
      >
        <EmailField />
        <SubscribeToNewsletterCheckbox />
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
    </FormProvider>
  );
};

export default LiveDemoForm;
