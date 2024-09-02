import { FormControl } from "@mui/material";
import { useFormContext } from "react-hook-form";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import { FIELD_NAMES } from "../constants";

type PerspectiveOverrideWarningProps = {
  perspectiveNames: string[];
};

const PerspectiveOverrideWarning = ({ perspectiveNames }: PerspectiveOverrideWarningProps) => {
  const { watch } = useFormContext();

  const perspectiveName = watch(FIELD_NAMES.NAME);

  return perspectiveNames.includes(perspectiveName) ? (
    <FormControl>
      <InlineSeverityAlert
        messageId="perspectiveOverrideWarning"
        messageValues={{
          perspectiveName,
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    </FormControl>
  ) : null;
};

export default PerspectiveOverrideWarning;
