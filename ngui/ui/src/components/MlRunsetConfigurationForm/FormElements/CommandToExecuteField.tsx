import FormHelperText from "@mui/material/FormHelperText";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { makeStyles } from "tss-react/mui";
import CodeEditor from "components/CodeEditor";
import { notOnlyWhiteSpaces } from "utils/validation";

const useStyles = makeStyles()((theme) => ({
  borderDiv: {
    position: "absolute",
    bottom: 0,
    right: 0,
    left: 0,
    top: 0,
    borderRadius: "4px",
    pointerEvents: "none",
    border: `1px solid ${theme.palette.error.light}`
  },
  codeToExecuteFieldError: {
    "&:focus-within": {
      "+ div": {
        borderWidth: "2px"
      }
    }
  }
}));

export const FIELD_NAME = "codeToExecute";

const CommandToExecuteField = () => {
  const intl = useIntl();

  const { classes } = useStyles();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  const isError = !!errors?.[FIELD_NAME];

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        validate: {
          notOnlyWhiteSpaces
        }
      }}
      render={({ field: { value, onChange, onBlur, ref } }) => (
        <>
          <div style={{ position: "relative" }}>
            <CodeEditor
              value={value}
              language="bash"
              className={classes.codeToExecuteFieldError}
              placeholder={intl.formatMessage({ id: "pleaseEnterShellCommands" })}
              onChange={onChange}
              onBlur={onBlur}
              style={{
                minHeight: "85px"
              }}
              ref={ref}
            />
            {isError && <div className={classes.borderDiv} />}
          </div>
          {isError && <FormHelperText error>{errors[FIELD_NAME].message}</FormHelperText>}
        </>
      )}
    />
  );
};

export default CommandToExecuteField;
