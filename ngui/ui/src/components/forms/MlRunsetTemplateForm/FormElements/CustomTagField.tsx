import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { SPACING_1 } from "utils/layouts";
import { FIELD_NAMES } from "../constants";

export const KEY_FIELD_NAME = FIELD_NAMES.TAG_KEY;
export const VALUE_FIELD_NAME = FIELD_NAMES.TAG_VALUE;

const CustomTagField = ({ isLoading = false }) => (
  <>
    <Box display="flex" gap={SPACING_1}>
      <Box flexGrow={1} flexBasis="150px">
        <TextInput
          name={KEY_FIELD_NAME}
          label={<FormattedMessage id="tagForCreatedResources" />}
          required
          dataTestId="input_custom_tag"
          isLoading={isLoading}
        />
      </Box>
      <Box flexGrow={2} flexBasis="200px">
        <TextInput name={VALUE_FIELD_NAME} label={<FormattedMessage id="customTagValue" />} required isLoading={isLoading} />
      </Box>
    </Box>
  </>
);

export default CustomTagField;
