import { ReactNode } from "react";
import Box from "@mui/material/Box";
import { useIntl } from "react-intl";
import QuestionMark from "components/QuestionMark";

type TitleType = { title: ReactNode; titleMessageId?: never } | { title?: never; titleMessageId: string };

type HeaderHelperCellProps = {
  helperMessageId: string;
  titleDataTestId?: string;
  helperMessageValues?: { [key: string]: ReactNode };
  onTooltipTitleClick?: () => void;
} & TitleType;

const HeaderHelperCell = ({
  title,
  titleMessageId,
  titleDataTestId,
  onTooltipTitleClick,
  helperMessageValues,
  helperMessageId
}: HeaderHelperCellProps) => {
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
