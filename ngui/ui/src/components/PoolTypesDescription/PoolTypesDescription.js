import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import DashedTypography from "components/DashedTypography";
import KeyValueLabel from "components/KeyValueLabel";
import PoolTypeIcon from "components/PoolTypeIcon";
import { POOL_TYPES } from "utils/constants";

const getPoolTypeHelperTextMessageId = (messageIdBase) => `${messageIdBase}PoolTypeDescription`;

const PoolTypesDescription = () => {
  const [shouldShowDescription, setShouldShowDescription] = useState(false);

  const renderTypesDescriptionMessage = (messageId) => (
    <DashedTypography
      dataTestId="label_types_description"
      gutterBottom
      onClick={() => setShouldShowDescription(!shouldShowDescription)}
    >
      <FormattedMessage id={messageId} />
    </DashedTypography>
  );

  return shouldShowDescription ? (
    <>
      {renderTypesDescriptionMessage("hideTypesDescription")}
      {Object.entries(POOL_TYPES).map(([type, messageIdBase]) => (
        <KeyValueLabel
          key={type}
          separator="hyphen"
          renderKey={() => <PoolTypeIcon type={type} />}
          value={<FormattedMessage id={getPoolTypeHelperTextMessageId(messageIdBase)} />}
          isBoldValue={false}
          dataTestIds={{
            key: `img_type_${type}`,
            value: `text_type_${type}`
          }}
          typographyProps={{
            gutterBottom: true
          }}
        />
      ))}
    </>
  ) : (
    renderTypesDescriptionMessage("showTypesDescription")
  );
};

export default PoolTypesDescription;
