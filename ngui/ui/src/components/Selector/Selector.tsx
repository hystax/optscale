import { ReactNode, forwardRef } from "react";
import { FormControl, FormHelperText, type SxProps } from "@mui/material";
import { useIntl } from "react-intl";
import { Select } from "./components";

type SelectorProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
  labelMessageId?: string;
  shrinkLabel?: boolean;
  required?: boolean;
  fullWidth?: boolean;
  helperText?: string;
  error?: boolean;
  margin?: "none" | "dense" | "normal" | undefined;
  sx?: SxProps;
  children: ReactNode;
  readOnly?: boolean;
  onBlur?: () => void;
  name?: string;
  variant?: "standard" | "outlined" | "filled" | undefined;
  disabled?: boolean;
  isLoading?: boolean;
  compact?: boolean;
  open?: boolean;
  onOpen?: () => void;
  onClose?: () => void;
  endAdornment?: ReactNode;
  renderValue?: (value: unknown) => ReactNode;
};

const APPROXIMATE_LABEL_SYMBOL_WIDTH = 11;

const Selector = forwardRef(
  (
    {
      value,
      onChange,
      labelMessageId,
      id,
      shrinkLabel,
      required = false,
      fullWidth = false,
      helperText,
      error = false,
      margin,
      sx,
      children,
      readOnly = false,
      onBlur,
      name,
      variant,
      disabled,
      isLoading,
      open,
      onOpen,
      onClose,
      endAdornment,
      renderValue
    }: SelectorProps,
    ref
  ) => {
    const intl = useIntl();

    const dataTestIds = {
      formControl: `${id}-form-control`,
      select: `${id}-select`,
      label: `${id}-label`,
      helper: `${id}-helper-text`
    };

    const label = labelMessageId ? intl.formatMessage({ id: labelMessageId }) : null;

    const approximateLabelWidth = (label?.length ?? 0) * APPROXIMATE_LABEL_SYMBOL_WIDTH;

    const getVariant = () => {
      if (isLoading) {
        return variant;
      }
      return readOnly ? "standard" : variant;
    };

    return (
      <FormControl
        variant={getVariant()}
        margin={margin}
        fullWidth={fullWidth}
        error={error}
        data-test-id={dataTestIds.formControl}
        sx={{
          minWidth: approximateLabelWidth,
          ...sx
        }}
      >
        <Select
          id={id}
          name={name}
          dataTestIds={{
            selectDataTestId: dataTestIds.select,
            labelDataTestId: dataTestIds.label
          }}
          value={value}
          required={required}
          onChange={onChange}
          onBlur={onBlur}
          label={label}
          inputRef={ref}
          shrinkLabel={shrinkLabel}
          disabled={disabled}
          isLoading={isLoading}
          readOnly={readOnly}
          open={open}
          onOpen={onOpen}
          onClose={onClose}
          endAdornment={endAdornment}
          renderValue={renderValue}
        >
          {children}
        </Select>
        {helperText && <FormHelperText data-test-id={dataTestIds.helper}>{helperText}</FormHelperText>}
      </FormControl>
    );
  }
);

export default Selector;
