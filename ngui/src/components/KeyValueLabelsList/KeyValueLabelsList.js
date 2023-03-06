import React from "react";
import PropTypes from "prop-types";
import KeyValueLabel from "components/KeyValueLabel";
import { isLastItem } from "utils/arrays";

const KeyValueLabelsList = ({ items = [] }) =>
  items.map(
    ({ itemKey, messageId, value, dataTestIds, typographyProps, show = true }, index) =>
      show && (
        <KeyValueLabel
          key={itemKey}
          typographyProps={{
            gutterBottom: !isLastItem(index, items.length),
            ...typographyProps
          }}
          value={value}
          messageId={messageId}
          dataTestIds={dataTestIds}
        />
      )
  );

KeyValueLabelsList.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({
      itemKey: PropTypes.string.isRequired,
      messageId: PropTypes.string.isRequired,
      typographyProps: PropTypes.object,
      value: PropTypes.node,
      dataTestIds: PropTypes.object
    })
  )
};

export default KeyValueLabelsList;
