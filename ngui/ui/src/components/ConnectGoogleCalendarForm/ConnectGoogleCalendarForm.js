import React from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import CopyText from "components/CopyText";
import Input from "components/Input";
import { DOCS_HYSTAX_OPTSCALE } from "urls";

const CALENDAR_ID = "calendarId";

const ConnectGoogleCalendarForm = ({ serviceAccount, onCancel, onSubmit, isLoading }) => {
  const intl = useIntl();

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm({
    defaultValues: {
      [CALENDAR_ID]: ""
    }
  });

  return (
    <form onSubmit={handleSubmit((formData) => onSubmit(formData[CALENDAR_ID]))} noValidate>
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
        <Input
          required
          error={!!errors[CALENDAR_ID]}
          helperText={errors[CALENDAR_ID] && errors[CALENDAR_ID].message}
          label={<FormattedMessage id="calendarId" />}
          {...register(CALENDAR_ID, {
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            }
          })}
        />
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
        <Button messageId="cancel" variant="outlined" onClick={(event) => onCancel(event)} />
      </Box>
    </form>
  );
};

ConnectGoogleCalendarForm.propTypes = {
  serviceAccount: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default ConnectGoogleCalendarForm;
