import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import CopyText from "components/CopyText";
import { DOCS_HYSTAX_OPTSCALE } from "urls";
import { CalendarIdField } from "./FormElements";
import { ConnectGoogleCalendarFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const ConnectGoogleCalendarForm = ({
  serviceAccount,
  onCancel,
  onSubmit,
  isLoading = false
}: ConnectGoogleCalendarFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit((formData) => onSubmit(formData.calendarId))} noValidate>
        <Box mb={2}>
          <Typography>
            <FormattedMessage id="integrationsGoogleCalendarDescription1" />
          </Typography>
        </Box>
        <Box mb={2}>
          <Box mb={1}>
            <Typography>
              <FormattedMessage
                id="toConnectGoogleCalendarToOptScale"
                values={{
                  br: <br />,
                  strong: (chunks) => <strong>{chunks}</strong>,
                  link: (
                    <CopyText variant="inherit" text={serviceAccount}>
                      {serviceAccount}
                    </CopyText>
                  )
                }}
              />
            </Typography>
          </Box>
          <CalendarIdField />
        </Box>
        <Box mb={2}>
          <Typography>
            <FormattedMessage
              id="ifYouNeedMoreDescription"
              values={{
                link: (chunks) => (
                  <Link data-test-id="link_read_more" href={DOCS_HYSTAX_OPTSCALE} target="_blank" rel="noopener">
                    {chunks}
                  </Link>
                )
              }}
            />
          </Typography>
        </Box>
        <Box display="flex">
          <ButtonLoader color="primary" variant="contained" messageId="connect" isLoading={isLoading} type="submit" />
          <Button messageId="cancel" variant="outlined" onClick={onCancel} />
        </Box>
      </form>
    </FormProvider>
  );
};

export default ConnectGoogleCalendarForm;
