import Box from "@mui/material/Box";
import { useIntl } from "react-intl";
import QuestionMark from "components/QuestionMark";

const HeaderHelperCell = ({
  title,
  titleMessageId,
  titleDataTestId,
  helperMessageId,
  helperMessageValues,
  onTooltipTitleClick
}) => {
  const intl = useIntl();

  return (
    <Box width="max-content" display="flex" alignItems="center">
      <span data-test-id={titleDataTestId}>{title ?? intl.formatMessage({ id: titleMessageId })}</span>
      <QuestionMark
        messageId={helperMessageId}
        messageValues={helperMessageValues}
        fontSize="small"
        onTooltipTitleClick={onTooltipTitleClick}
      />
    </Box>
  );
};

export default HeaderHelperCell;
