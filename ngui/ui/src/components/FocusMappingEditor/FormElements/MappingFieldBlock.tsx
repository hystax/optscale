import { ReactNode, useEffect } from "react";
import { Box, Paper, Typography } from "@mui/material";
import { Controller, useFormContext, useWatch } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import { Checkbox } from "components/forms/common/fields";
import { SPACING_1, SPACING_2 } from "utils/layouts";
import MappingChainFieldArray from "./MappingChainFieldArray";

type MappingFieldBlockProps = {
  // Path of the mapping field in the form values, e.g. "focusMapping.cost"
  name: string;
  labelMessageId: string;
  dataTestId: string;
  // Field-level parameters shown above the chain, e.g. the mode of the tags
  beforeChain?: ReactNode;
  // Field-level parameters shown below the chain, e.g. the decimal separator of the cost
  children?: ReactNode;
  // The field takes no source, e.g. the tags in prefixed_columns mode
  hideChain?: boolean;
  // The field cannot end with the default mapping, e.g. the tags outside json mode
  hideUseDefaultAtEnd?: boolean;
};

// A card of one mapping field: auto-detected, or customized with a chain of steps shown right under the header
const MappingFieldBlock = ({
  name,
  labelMessageId,
  dataTestId,
  beforeChain,
  children,
  hideChain = false,
  hideUseDefaultAtEnd = false,
}: MappingFieldBlockProps) => {
  const { control, clearErrors } = useFormContext();

  const isEnabled: boolean = useWatch({ control, name: `${name}.enabled` });

  // The inputs of an auto-detected field are unmounted and not sent, so their errors no longer apply
  useEffect(() => {
    if (!isEnabled) {
      clearErrors(name);
    }
  }, [isEnabled, clearErrors, name]);

  return (
    <Paper variant="outlined" data-test-id={dataTestId}>
      <Box display="flex" justifyContent="space-between" alignItems="center" gap={SPACING_1} px={SPACING_2} py={SPACING_1}>
        <Typography variant="body1" color="primary">
          <FormattedMessage id={labelMessageId} />
        </Typography>
        <Controller
          name={`${name}.enabled`}
          control={control}
          render={({ field: { value, onChange } }) => (
            <ButtonGroup
              buttons={[
                {
                  id: "autoDetect",
                  messageId: "focusMappingAutoDetect",
                  dataTestId: `btn_${dataTestId}_auto_detect`,
                  action: () => onChange(false),
                },
                {
                  id: "custom",
                  messageId: "custom",
                  dataTestId: `btn_${dataTestId}_custom`,
                  action: () => onChange(true),
                },
              ]}
              activeButtonId={value ? "custom" : "autoDetect"}
              activeButtonIndex={undefined}
              fullWidth={false}
            />
          )}
        />
      </Box>
      {isEnabled && (
        <Box px={SPACING_2} pb={SPACING_1}>
          {beforeChain}
          {!hideChain && <MappingChainFieldArray fieldName={name} />}
          {!hideChain && !hideUseDefaultAtEnd && (
            <Checkbox name={`${name}.useDefaultAtEnd`} label={<FormattedMessage id="focusMappingUseDefaultAtEnd" />} />
          )}
          {children}
        </Box>
      )}
    </Paper>
  );
};

export default MappingFieldBlock;
