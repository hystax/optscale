import TouchAppIcon from "@mui/icons-material/TouchApp";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import SummaryCard from "components/SummaryCard/SummaryCard";
import SummaryCardContent from "components/SummaryCardContent";
import { SPACING_1 } from "utils/layouts";
import { isEmpty } from "utils/objects";

const SummaryCardExtended = ({
  value,
  caption,
  relativeValue,
  relativeValueCaption,
  dataTestIds,
  color = "primary",
  isLoading = false,
  help = {},
  icon = {},
  button = {},
  backdrop
}) => {
  const content = (
    <Box display="flex" height="100%">
      <div>
        <SummaryCardContent {...{ value, caption, dataTestIds, icon, help, button }} />
      </div>
      <Divider flexItem orientation="vertical" sx={{ mx: SPACING_1 }} />
      <div>
        <SummaryCardContent
          {...{ value: relativeValue, caption: relativeValueCaption, dataTestIds: {}, icon: {}, help: {}, button: {} }}
        />
      </div>
      {!isEmpty(button) && (
        <Box position="absolute" top={SPACING_1} right={SPACING_1}>
          <TouchAppIcon color="info" sx={{ opacity: 0.5 }} />
        </Box>
      )}
    </Box>
  );

  return (
    <SummaryCard
      customContent={content}
      {...{
        dataTestIds,
        color,
        isLoading,
        backdrop,
        button
      }}
    />
  );
};

export default SummaryCardExtended;
