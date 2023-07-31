import React from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";

const REPORT_REQUESTOR_ID = "reportRequestorId";

const ReportRequestorIdField = () => {
  const {
    register,
    formState: { errors }
  } = useFormContext();
  const intl = useIntl();

  return (
    <Input
      name={REPORT_REQUESTOR_ID}
      label={<FormattedMessage id={REPORT_REQUESTOR_ID} />}
      required
      error={!!errors[REPORT_REQUESTOR_ID]}
      helperText={errors[REPORT_REQUESTOR_ID] && errors[REPORT_REQUESTOR_ID].message}
      {...register(REPORT_REQUESTOR_ID, {
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        pattern: {
          value: /^TARID-[0-9a-f]{6}$/,
          message: intl.formatMessage({ id: "pleaseProvideValidReportRequestorId" })
        }
      })}
      dataTestId="input_name"
    />
  );
};

export default ReportRequestorIdField;
