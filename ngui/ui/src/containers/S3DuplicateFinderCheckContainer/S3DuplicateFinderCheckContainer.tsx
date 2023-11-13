import { useParams } from "react-router-dom";
import S3DuplicateFinderCheck from "components/S3DuplicateFinderCheck";
import { useS3DuplicatesSettings } from "hooks/useS3DuplicatesSettings";
import S3DuplicatesService from "services/S3DuplicatesService";

const S3DuplicateFinderCheckContainer = () => {
  const { checkId } = useParams();

  const { useGet } = S3DuplicatesService();

  const { gemini, isLoading: isGetCheckLoading } = useGet(checkId);

  const {
    isLoading: isGetSettingsLoading,
    settings: { thresholds }
  } = useS3DuplicatesSettings();

  return (
    <S3DuplicateFinderCheck
      gemini={gemini}
      isLoadingProps={{
        isGetCheckLoading,
        isGetSettingsLoading
      }}
      thresholds={thresholds}
    />
  );
};

export default S3DuplicateFinderCheckContainer;
