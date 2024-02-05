import { type ReactNode, type Ref } from "react";
import { InputAdornment, InputLabel, Select as MuiSelect, Skeleton } from "@mui/material";
import Item from "../Item";
import useStyles from "./Select.styles";

const LOADING_ITEM_VALUE = "loading";

type SelectProps = {
  id: string;
  value: string;
  onChange: (value: string) => void;
  children: ReactNode;
  name?: string;
  required?: boolean;
  label?: ReactNode;
  dataTestIds: {
    selectDataTestId: string;
    labelDataTestId?: string;
  };
  shrinkLabel?: boolean;
  onBlur?: () => void;
  disabled?: boolean;
  isLoading?: boolean;
  readOnly?: boolean;
  inputRef?: Ref<unknown>;
  open?: boolean;
  onOpen?: () => void;
  onClose?: () => void;
  endAdornment?: ReactNode;
};

const Select = ({
  id,
  name,
  required,
  label,
  dataTestIds,
  value,
  onChange,
  children,
  shrinkLabel,
  onBlur,
  inputRef,
  disabled,
  isLoading,
  readOnly,
  open,
  onClose,
  onOpen,
  endAdornment
}: SelectProps) => {
  const { classes } = useStyles();

  const { selectDataTestId, labelDataTestId } = dataTestIds;

  const handleChange = (event) => {
    if (event.target.value) {
      onChange(event.target.value);
    }
  };

  return (
    <>
      {label && (
        <InputLabel id={`${id}-selector-label`} shrink={shrinkLabel} required={required} data-test-id={labelDataTestId}>
          {label}
        </InputLabel>
      )}
      <MuiSelect
        id={id}
        name={name}
        labelId={label ? `${id}-selector-label` : undefined}
        data-test-id={selectDataTestId}
        value={isLoading ? LOADING_ITEM_VALUE : value}
        onChange={isLoading ? undefined : handleChange}
        label={label}
        notched={shrinkLabel}
        onBlur={onBlur}
        IconComponent={readOnly && !isLoading ? () => null : undefined}
        inputRef={inputRef}
        disabled={isLoading || disabled}
        open={open}
        classes={{
          root: readOnly ? classes.readOnly : "",
          icon: endAdornment ? classes.adornmentIconPosition : ""
        }}
        onOpen={onOpen}
        onClose={onClose}
        MenuProps={{
          classes: {
            root: classes.menu
          }
        }}
        endAdornment={endAdornment && <InputAdornment position="end">{endAdornment}</InputAdornment>}
        readOnly={!isLoading && readOnly}
      >
        {isLoading
          ? [
              <Item key="loading" value={LOADING_ITEM_VALUE}>
                <Skeleton width="100%" />
              </Item>
            ]
          : children}
      </MuiSelect>
    </>
  );
};

export default Select;
