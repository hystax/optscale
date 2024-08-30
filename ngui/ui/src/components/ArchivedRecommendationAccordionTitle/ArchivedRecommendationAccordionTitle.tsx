import { ReactNode } from "react";
import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Chip from "components/Chip";
import KeyValueLabel from "components/KeyValueLabel";
import { ARCHIVATION_REASON_MESSAGE_ID } from "utils/constants";
import { EN_FULL_FORMAT, formatUTC } from "utils/datetime";

type ArchivedRecommendationAccordionTitleProps = {
  titleMessageId: string;
  reason: keyof typeof ARCHIVATION_REASON_MESSAGE_ID;
  count: number;
  archivedAt: number;
  dataTestId?: string;
};

type StyledKeyValueChipProps = {
  keyMessageId: string;
  value: ReactNode;
};

const StyledKeyValueChip = ({ keyMessageId, value }: StyledKeyValueChipProps) => (
  <Chip
    multiline
    variant="outlined"
    sx={{
      // Override the border color to make it contrast with the background when an accordion is expanded
      borderColor: (theme) => theme.palette.info.dark
    }}
    label={
      // Wrap with typography to inherit its text color setting to make the label contrast with the background
      <Typography>
        <KeyValueLabel keyMessageId={keyMessageId} isBoldValue={false} value={value} />
      </Typography>
    }
  />
);

const ArchivedRecommendationAccordionTitle = ({
  titleMessageId,
  reason,
  count,
  archivedAt,
  dataTestId
}: ArchivedRecommendationAccordionTitleProps) => (
  <Box display="flex" flexWrap="wrap" alignItems="center" columnGap={1} rowGap={0.5} pb={1} pt={1} data-test-id={dataTestId}>
    <Typography>
      <FormattedMessage id={titleMessageId} />
    </Typography>
    <Box display="flex" gap={0.5} flexWrap="wrap">
      <StyledKeyValueChip keyMessageId="count" value={count} />
      <StyledKeyValueChip
        keyMessageId="reason"
        value={<FormattedMessage id={ARCHIVATION_REASON_MESSAGE_ID[reason] ?? "unknown"} />}
      />
      <StyledKeyValueChip keyMessageId="archivedAt" value={`${formatUTC(archivedAt, EN_FULL_FORMAT)} UTC`} />
    </Box>
  </Box>
);

export default ArchivedRecommendationAccordionTitle;
