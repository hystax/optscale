import { ReactNode, forwardRef } from "react";
import { Box } from "@mui/material";
import Typography, { TypographyOwnProps } from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";

type KeyValueLabelProps = {
  value: ReactNode;
  variant: TypographyOwnProps["variant"];
  keyMessageId?: string;
  keyText?: string;
  isBoldValue?: boolean;
  dataTestIds?: {
    typography?: string;
    key?: string;
    value?: string;
  };
  gutterBottom?: boolean;
  sx?: Record<string, unknown>;
};

const KeyValueLabel = forwardRef<HTMLDivElement, KeyValueLabelProps>(
  ({ value, variant, keyMessageId, keyText, isBoldValue = true, dataTestIds = {}, sx = {}, gutterBottom = false }, ref) => {
    const renderValue = () => {
      if (value || value === 0) {
        return value;
      }

      return <>&nbsp;-&nbsp;</>;
    };

    const renderKey = () => {
      if (keyMessageId) {
        return <FormattedMessage id={keyMessageId} />;
      }

      return keyText;
    };

    const { typography: typographyDataTestId, key: keyDataTestId, value: valueDataTestId } = dataTestIds;

    return (
      <Typography
        ref={ref}
        data-test-id={typographyDataTestId}
        component="div"
        variant={variant}
        gutterBottom={gutterBottom}
        sx={{
          display: "flex",
          alignItems: "center",
          flexWrap: "wrap",
          ...sx
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexWrap: "nowrap",
            whiteSpace: "normal",
            overflowWrap: "anywhere"
          }}
          data-test-id={keyDataTestId}
        >
          {renderKey()}
          {<>:&nbsp;</>}
        </Box>
        <Box
          sx={{
            display: "flex",
            whiteSpace: "normal",
            overflowWrap: "anywhere",
            fontWeight: isBoldValue ? "bold" : undefined
          }}
          data-test-id={valueDataTestId}
        >
          {renderValue()}
        </Box>
      </Typography>
    );
  }
);

export default KeyValueLabel;
