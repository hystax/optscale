import React from "react";
import { FormattedMessage } from "react-intl";
import { EMPTY_UUID } from "utils/constants";

const TaggingPolicyDescriptionShort = ({ conditions }) => {
  const strong = (chunks) => <strong>{chunks}</strong>;
  const { tag: prohibitedTag, without_tag: requiredTag } = conditions;
  if (prohibitedTag === EMPTY_UUID) {
    return <FormattedMessage id="taggingPolicy.anyTagsShort" />;
  }

  if (!prohibitedTag) {
    return <FormattedMessage id="taggingPolicy.requiredTagDescriptionShort" values={{ requiredTag, strong }} />;
  }

  if (!requiredTag) {
    return <FormattedMessage id="taggingPolicy.prohibitedTagDescriptionShort" values={{ prohibitedTag, strong }} />;
  }

  return (
    <FormattedMessage
      id="taggingPolicy.tagsCorrelationDescriptionShort"
      values={{ firstTag: prohibitedTag, secondTag: requiredTag, strong }}
    />
  );
};

export default TaggingPolicyDescriptionShort;
