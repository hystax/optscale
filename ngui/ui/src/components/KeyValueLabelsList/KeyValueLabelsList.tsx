import KeyValueLabel from "components/KeyValueLabel";
import { isLastItem } from "utils/arrays";

const KeyValueLabelsList = ({ items = [] }) =>
  items.map(
    ({ itemKey, renderKey, messageId, text, value, dataTestIds, typographyProps, show = true, isBoldValue }, index) =>
      show && (
        <KeyValueLabel
          key={itemKey}
          renderKey={renderKey}
          typographyProps={{
            gutterBottom: !isLastItem(index, items.length),
            ...typographyProps
          }}
          value={value}
          text={text}
          messageId={messageId}
          dataTestIds={dataTestIds}
          isBoldValue={isBoldValue}
        />
      )
  );

export default KeyValueLabelsList;
