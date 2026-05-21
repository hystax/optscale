import { type FormEventHandler, useState } from "react";
import { Box, Tab, Tabs } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { type TagSelector } from "services/PowerScheduleService";
import { TABS } from "./constants";
import { ByTagsTab, DataSourcesField, FiltersField, FormButtons, InstancesField } from "./FormElements";

type AddInstancesToScheduleFormProps = {
  onSubmit: FormEventHandler;
  onSubmitByTags: () => void;
  onRemoveTagFilter?: () => void;
  instances: unknown[];
  onCancel: () => void;
  filterValues: unknown;
  instancesCountLimit: number;
  existingTagSelector?: TagSelector | null;
  isLoadingProps?: {
    isSubmitLoading?: boolean;
    isGetInstancesLoading?: boolean;
    isGetFilterValuesLoading?: boolean;
    isUpdateLoading?: boolean;
  };
};

const AddInstancesToScheduleForm = ({
  onSubmit,
  onSubmitByTags,
  onRemoveTagFilter,
  instances,
  onCancel,
  filterValues,
  instancesCountLimit,
  existingTagSelector,
  isLoadingProps = {},
}: AddInstancesToScheduleFormProps) => {
  const {
    isSubmitLoading = false,
    isGetInstancesLoading = false,
    isGetFilterValuesLoading = false,
    isUpdateLoading = false,
  } = isLoadingProps;

  const [activeTab, setActiveTab] = useState(TABS.MANUAL);

  return (
    <form onSubmit={activeTab === TABS.MANUAL ? onSubmit : (e) => e.preventDefault()} noValidate>
      <DataSourcesField />
      <Box sx={{ borderBottom: 1, borderColor: "divider", mt: 1, mb: 2 }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
          <Tab label={<FormattedMessage id="addManually" />} value={TABS.MANUAL} />
          <Tab label={<FormattedMessage id="byTagsAws" />} value={TABS.BY_TAGS} />
        </Tabs>
      </Box>
      {activeTab === TABS.MANUAL && (
        <>
          <FiltersField filterValues={filterValues} isLoading={isGetFilterValuesLoading} />
          <InstancesField instances={instances} isLoading={isGetInstancesLoading} instancesCountLimit={instancesCountLimit} />
          <FormButtons onCancel={onCancel} isLoading={isSubmitLoading} />
        </>
      )}
      {activeTab === TABS.BY_TAGS && (
        <ByTagsTab
          onSubmitByTags={onSubmitByTags}
          isSubmitLoading={isUpdateLoading}
          onCancel={onCancel}
          existingTagSelector={existingTagSelector}
          onRemoveTagFilter={onRemoveTagFilter}
        />
      )}
    </form>
  );
};

export default AddInstancesToScheduleForm;
