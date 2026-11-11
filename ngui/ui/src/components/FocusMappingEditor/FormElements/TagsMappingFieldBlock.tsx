import { useFormContext, useWatch } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { TAGS_MODES } from "../constants";
import { canTagsUseDefault } from "../mapping";
import type { TagsMode } from "../types";
import MappingFieldBlock from "./MappingFieldBlock";
import TagsModeField from "./TagsModeField";

type TagsMappingFieldBlockProps = {
  // Path of the tags field in the form values, e.g. "focusMapping.tags"
  name: string;
  labelMessageId: string;
  dataTestId: string;
};

// Tags are read in json or list mode from a chain of steps, or in prefixed_columns mode from every column with a prefix
const TagsMappingFieldBlock = ({ name, labelMessageId, dataTestId }: TagsMappingFieldBlockProps) => {
  const { control } = useFormContext();

  const mode: TagsMode | null = useWatch({ control, name: `${name}.mode` });

  const isPrefixedColumns = mode === TAGS_MODES.PREFIXED_COLUMNS;

  return (
    <MappingFieldBlock
      name={name}
      labelMessageId={labelMessageId}
      dataTestId={dataTestId}
      hideChain={isPrefixedColumns}
      hideUseDefaultAtEnd={!canTagsUseDefault(mode)}
      beforeChain={
        <>
          <TagsModeField name={`${name}.mode`} />
          {isPrefixedColumns && (
            <TextInput
              name={`${name}.prefix`}
              required
              // The API accepts any non-empty prefix, a blank one included, of any length
              maxLength={null}
              validate={{ notOnlyWhiteSpaces: () => true }}
              dataTestId={`input_${name}.prefix`}
              label={<FormattedMessage id="focusMappingTagsPrefix" />}
              placeholder="tag."
              InputProps={{
                endAdornment: <QuestionMark messageId="focusMappingTagsPrefixTooltip" dataTestId={`qmark_${name}.prefix`} />,
              }}
            />
          )}
        </>
      }
    />
  );
};

export default TagsMappingFieldBlock;
