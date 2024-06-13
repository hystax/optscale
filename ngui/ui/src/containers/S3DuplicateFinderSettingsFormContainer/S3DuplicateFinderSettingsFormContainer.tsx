import S3DuplicateFinderSettingsForm from "components/forms/S3DuplicateFinderSettingsForm";
import { FormValues } from "components/forms/S3DuplicateFinderSettingsForm/types";
import { useS3DuplicatesSettings } from "hooks/useS3DuplicatesSettings";
import OrganizationOptionsService from "services/OrganizationOptionsService";

const S3DuplicateFinderSettingsFormContainer = ({ closeSideModal }) => {
  const {
    isLoading: isGetDataLoading,
    settings: {
      thresholds: { requiringAttention, critical }
    }
  } = useS3DuplicatesSettings();

  const { useUpdateS3DuplicatedOrganizationSettings } = OrganizationOptionsService();

  const { onUpdate, isLoading: isUpdateLoading } = useUpdateS3DuplicatedOrganizationSettings();

  const onSubmit = (formData: FormValues) => {
    onUpdate({
      thresholds: {
        requiring_attention: Number(formData.requiringAttention),
        critical: Number(formData.critical)
      }
    }).then(closeSideModal);
  };

  return (
    <S3DuplicateFinderSettingsForm
      requiringAttention={requiringAttention}
      critical={critical}
      onCancel={closeSideModal}
      onSubmit={onSubmit}
      isLoadingProps={{
        isGetDataLoading,
        isSubmitLoading: isUpdateLoading
      }}
    />
  );
};

export default S3DuplicateFinderSettingsFormContainer;
