import { ReactNode } from "react";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import SelectorComponent, { Item } from "components/Selector";
import { idx } from "utils/objects";

type SelectorProps = {
  name: string;
  items: {
    value: string;
    content: ReactNode;
    depth?: number;
    disabled?: boolean | ((field: { value: string }) => boolean);
  }[];
  labelMessageId: string;
  defaultValue?: string;
  id?: string;
  disabled?: boolean;
  fullWidth?: boolean;
  required?: boolean;
  isLoading?: boolean;
  onChange?: (value: string) => void;
  readOnly?: boolean;
  endAdornment?: ReactNode;
  validate?: Record<string, unknown>;
  helperText?: ReactNode;
  shouldUnregister?: boolean;
};

const Selector = ({
  name,
  items,
  labelMessageId,
  defaultValue,
  id,
  disabled = false,
  fullWidth = false,
  required = false,
  isLoading = false,
  onChange,
  readOnly = false,
  endAdornment,
  validate,
  helperText,
  shouldUnregister
}: SelectorProps) => {
  const {
    formState: { errors },
    control
  } = useFormContext();

  const intl = useIntl();

  const fieldError = idx(name.split("."), errors);

  return (
    <Controller
      name={name}
      control={control}
      shouldUnregister={shouldUnregister}
      defaultValue={defaultValue}
      rules={{
        required: {
          value: required,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        validate
      }}
      render={({ field }) => (
        <SelectorComponent
          id={id ?? `${name}-selector`}
          disabled={disabled}
          fullWidth={fullWidth}
          labelMessageId={labelMessageId}
          required={required}
          error={!!fieldError}
          helperText={fieldError ? fieldError?.message : helperText}
          isLoading={isLoading}
          readOnly={readOnly}
          endAdornment={endAdornment}
          {...field}
          onChange={(newValue) => {
            field.onChange(newValue);
            if (typeof onChange === "function") {
              onChange(newValue);
            }
          }}
        >
          {items.map(({ value, content, depth, disabled: itemDisabled }) => (
            <Item
              key={value}
              value={value}
              depth={depth}
              disabled={typeof itemDisabled === "function" ? itemDisabled(field) : itemDisabled}
            >
              {content}
            </Item>
          ))}
        </SelectorComponent>
      )}
    />
  );
};

export default Selector;
