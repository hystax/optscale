import { useState, Fragment } from "react";
import { Box, Checkbox, Divider, FormControlLabel, FormGroup, Typography, Paper, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import ButtonLoader from "components/ButtonLoader";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { OPTSCALE_MODE } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

type ModeWrapperProps = {
  option: Record<(typeof OPTSCALE_MODE)[keyof typeof OPTSCALE_MODE], boolean>;
  onApply: (mode: ModeWrapperProps["option"]) => void;
  isLoadingProps?: {
    isGetOrganizationOptionLoading?: boolean;
    isUpdateOrganizationOptionLoading?: boolean;
  };
};

type FeatureListProps = {
  messageIds: string[];
};

type CardProps = {
  name: string;
  messageIds: FeatureListProps["messageIds"];
  onSelect: () => void;
  isSelected?: boolean;
  isLoading?: boolean;
};

const FeatureList = ({ messageIds }: FeatureListProps) =>
  messageIds.map((messageId) => (
    <Fragment key={messageId}>
      <Typography>
        {" - "}
        <FormattedMessage id={messageId} />
      </Typography>
    </Fragment>
  ));

const Card = ({ name, messageIds, onSelect, isSelected, isLoading }: CardProps) => (
  <ContentBackdropLoader isLoading={isLoading}>
    <Paper elevation={0}>
      <Box
        sx={{
          padding: "1rem"
        }}
      >
        <div>
          <FormGroup>
            <FormControlLabel
              control={<Checkbox checked={isSelected} onChange={onSelect} />}
              label={<FormattedMessage id={name} />}
              slotProps={{ typography: { variant: "body1" } }}
            />
          </FormGroup>
        </div>
        <div>
          <FeatureList messageIds={messageIds} />
        </div>
      </Box>
    </Paper>
  </ContentBackdropLoader>
);

const Mode = ({ option, onApply, isLoadingProps = {} }: ModeWrapperProps) => {
  const { isGetOrganizationOptionLoading, isUpdateOrganizationOptionLoading } = isLoadingProps;

  const [mode, setModeState] = useState({
    [OPTSCALE_MODE.FINOPS]: option?.[OPTSCALE_MODE.FINOPS] ?? true,
    [OPTSCALE_MODE.MLOPS]: option?.[OPTSCALE_MODE.MLOPS] ?? true
  });

  const setMode = (value: keyof ModeWrapperProps["option"]) => {
    setModeState((currentState) => ({ ...currentState, [value]: !currentState[value] }));
  };

  return (
    <>
      <Stack direction="row" spacing={SPACING_2}>
        <Card
          name="mlops"
          isSelected={mode[OPTSCALE_MODE.MLOPS]}
          onSelect={() => setMode(OPTSCALE_MODE.MLOPS)}
          isLoading={isGetOrganizationOptionLoading}
          messageIds={["mode.mlops.1", "mode.mlops.2", "mode.mlops.3", "mode.mlops.4", "mode.mlops.5", "mode.mlops.6"]}
        />
        <Divider orientation="vertical" flexItem />
        <Card
          name="finops"
          isSelected={mode[OPTSCALE_MODE.FINOPS]}
          isLoading={isGetOrganizationOptionLoading}
          onSelect={() => setMode(OPTSCALE_MODE.FINOPS)}
          messageIds={["mode.finops.1", "mode.finops.2", "mode.finops.3", "mode.finops.4", "mode.finops.5", "mode.finops.6"]}
        />
      </Stack>
      <FormButtonsWrapper>
        <ButtonLoader
          messageId="apply"
          size="small"
          color="primary"
          variant="contained"
          onClick={() => onApply(mode)}
          isLoading={isGetOrganizationOptionLoading || isUpdateOrganizationOptionLoading}
        />
      </FormButtonsWrapper>
    </>
  );
};

export default Mode;
