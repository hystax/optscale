import { FormHelperText, Input, Skeleton, Typography } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { MAX_INT_32 } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";
import { isWhitespaceString } from "utils/strings";
import { isPositiveNumberOrZero, isWholeNumber, lessOrEqual, notOnlyWhiteSpaces } from "utils/validation";

const TextWithInlineInput = ({
  name,
  messageId,
  messageValues = {},
  maxWidth = "50px",
  lessOrEqualValidation = lessOrEqual(MAX_INT_32),
  isLoading = false,
  ...rest
}) => {
  const intl = useIntl();

  const {
    register,
    formState: { errors }
  } = useFormContext();

  const error = errors[name] ?? {};
  const isError = !isEmptyObject(error);

  const input = (
    <Input
      style={{ margin: 0, maxWidth }}
      error={isError}
      inputProps={{ style: { padding: "0", textAlign: "center" } }}
      {...rest}
    />
  );

  const getInput = () => {
    const registerProps = register(name, {
      // valueAsNumber converts a string with only white spaces to 0, so the notOnlyWhiteSpaces validation wont work with valueAsNumber=true
      // so we keep the value as is and just add the notOnlyWhiteSpaces validation
      setValueAs: (value) => {
        if (value === "" || isWhitespaceString(value)) {
          // Return "" in order to trigger "required" validation
          // Return string containing only whitespace characters in order to trigger "white-spaces" validation
          return value;
        }
        return +value;
      },
      required: {
        value: true,
        message: intl.formatMessage({ id: "thisFieldIsRequired" })
      },
      validate: {
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true),
        moreOrEqualZero: (value) =>
          isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "moreOrEqual" }, { min: 0 }),
        lessOrEqualValidation,
        notOnlyWhiteSpaces
      }
    });
    return (
      <Input
        style={{ margin: 0, maxWidth }}
        error={isError}
        inputProps={{ style: { padding: "0", textAlign: "center" } }}
        {...registerProps}
      />
    );
  };

  return (
    <Typography component="div">
      <FormattedMessage
        id={messageId}
        values={{
          ...messageValues,
          input: isLoading ? <Skeleton sx={{ display: "inline-flex" }}>{input}</Skeleton> : getInput()
        }}
      />
      {isError && <FormHelperText error>{error.message}</FormHelperText>}
    </Typography>
  );
};

export default TextWithInlineInput;
