import { Box, Typography } from "@mui/material";
import { useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { SPACING_2 } from "utils/layouts";
import { FIELD_NAMES, REASONS } from "../constants";
import { FormValues } from "../types";
import MissingCapabilitiesField from "./MissingCapabilitiesField";
import OtherReasonField from "./OtherReasonField";
import ReasonsRadioGroup from "./ReasonsRadioGroup";

const Survey = () => {
  const { watch } = useFormContext<FormValues>();

  const reason = watch(FIELD_NAMES.REASON);

  return (
    <>
      <Typography marginBottom={SPACING_2}>
        <FormattedMessage id="disconnectingLastDataSource" />
      </Typography>
      <Box marginBottom={SPACING_2}>
        <ReasonsRadioGroup />
        {reason === REASONS.OTHER && <OtherReasonField />}
      </Box>
      <MissingCapabilitiesField />
    </>
  );
};

export default Survey;
