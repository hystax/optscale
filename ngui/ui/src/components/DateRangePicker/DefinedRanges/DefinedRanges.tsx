import { List, ListItem, ListItemText } from "@mui/material";
import { useIntl } from "react-intl";
import { isSameDay, secondsToMilliseconds } from "utils/datetime";
import { objectMap } from "utils/objects";

const isSameRange = (first, second) => {
  const { startDate: fStart, endDate: fEnd } = first;
  const { startDate: sStart, endDate: sEnd } = second;
  if (fStart && sStart && fEnd && sEnd) {
    return isSameDay(fStart, sStart) && isSameDay(fEnd, sEnd);
  }
  return false;
};

const DefinedRanges = ({ ranges, setRange, selectedRange }) => {
  const intl = useIntl();
  return (
    <List>
      {ranges.map((range) => (
        <ListItem button key={range.key} onClick={() => setRange(range)} data-test-id={range.dataTestId}>
          <ListItemText
            primaryTypographyProps={{
              style: {
                fontWeight: isSameRange(objectMap(range, secondsToMilliseconds), selectedRange) ? "bold" : "normal"
              }
            }}
          >
            {intl.formatMessage({ id: range.messageId })}
          </ListItemText>
        </ListItem>
      ))}
    </List>
  );
};

export default DefinedRanges;
