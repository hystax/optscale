import { useFormContext } from "react-hook-form";
import FormContentDescription from "components/FormContentDescription";
import { FIELD_NAMES } from "../constants";

type PerspectiveOverrideWarningProps = {
  perspectiveNames: string[];
};

const PerspectiveOverrideWarning = ({ perspectiveNames }: PerspectiveOverrideWarningProps) => {
  const { watch } = useFormContext();

  const perspectiveName = watch(FIELD_NAMES.NAME);

  return perspectiveNames.includes(perspectiveName) ? (
    <FormContentDescription
      alertProps={{
        messageId: "perspectiveOverrideWarning",
        messageValues: {
          perspectiveName,
          strong: (chunks) => <strong>{chunks}</strong>,
        },
      }}
    />
  ) : null;
};

export default PerspectiveOverrideWarning;
