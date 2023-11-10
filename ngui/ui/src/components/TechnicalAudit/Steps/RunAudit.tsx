import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import MailTo from "components/MailTo";
import RunTechnicalAuditForm from "components/RunTechnicalAuditForm";
import { EMAIL_SUPPORT } from "urls";
import { SPACING_1 } from "utils/layouts";

const RunAudit = ({ onRunAudit, isLoadingProps = {} }) => {
  // TODO: common issue on most forms - reportRequestorId is defined as a constant field name in a form, should take it from a single place
  const onSubmit = ({ reportRequestorId }) => {
    onRunAudit({ reportRequestorId, step: 1 });
  };

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12}>
        {/* TODO: probably need to remove p from app.json and component from here */}
        <Typography component="div">
          <FormattedMessage
            id="technicalAudit.runAuditDescription"
            values={{
              p: (chunks) => <p>{chunks}</p>,
              supportLink: (chunks) => <MailTo email={EMAIL_SUPPORT} text={chunks} />
            }}
          />
        </Typography>
      </Grid>
      <Grid item xs={12}>
        <RunTechnicalAuditForm onSubmit={onSubmit} isLoadingProps={isLoadingProps} />
      </Grid>
    </Grid>
  );
};

export default RunAudit;
