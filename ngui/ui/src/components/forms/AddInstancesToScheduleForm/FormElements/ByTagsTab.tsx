import { useEffect, useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import {
  Alert,
  Box,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  FormGroup,
  Stack,
  Typography,
} from "@mui/material";
import { useFieldArray, useFormContext, useWatch } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import IconButton from "components/IconButton";
import { TextInput } from "components/forms/common/fields";
import { useAllDataSources } from "hooks/coreData/useAllDataSources";
import { useDebouncedValue } from "hooks/useDebouncedValue";
import PowerScheduleService from "services/PowerScheduleService";
import { AWS_CNR } from "utils/constants";
import { SPACING_1, SPACING_2 } from "utils/layouts";
import { FIELD_NAMES } from "../constants";
import type { FormValues, TagEntry } from "../types";

type MatchedResource = {
  id: string;
  name: string;
  resource_type: string;
  region: string;
  stopped_allocated: string | boolean | null;
};

const RUNNING_STATES = new Set(["running", "available", "started", "active"]);
const STOPPED_STATES = new Set(["stopped", "paused", "terminated", "terminated_with_errors"]);

const StateLabel = ({ stopped_allocated }: { stopped_allocated: string | boolean | null }) => {
  if (stopped_allocated === true) return <FormattedMessage id="stopped" />;
  if (stopped_allocated === false) return <FormattedMessage id="running" />;
  if (typeof stopped_allocated === "string") {
    const lower = stopped_allocated.toLowerCase();
    if (RUNNING_STATES.has(lower)) return <FormattedMessage id="running" />;
    if (STOPPED_STATES.has(lower)) return <FormattedMessage id="stopped" />;
    const capitalized = lower.charAt(0).toUpperCase() + lower.slice(1);
    return <FormattedMessage id={lower} defaultMessage={capitalized} />;
  }
  return <FormattedMessage id="unknown" />;
};

const PreviewTable = ({ resources, isLoading }: { resources: MatchedResource[]; isLoading: boolean }) => {
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={2}>
        <CircularProgress size={22} />
      </Box>
    );
  }
  if (!resources.length) return null;

  return (
    <Box>
      <Typography variant="caption" color="text.secondary">
        <FormattedMessage id="matchingResources" values={{ count: resources.length }} />
      </Typography>
      <Box
        sx={{
          maxHeight: 220,
          overflowY: "auto",
          border: "1px solid",
          borderColor: "divider",
          borderRadius: 1,
          mt: 0.5,
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr style={{ background: "rgba(0,0,0,0.04)" }}>
              <th style={{ padding: "4px 8px", textAlign: "left" }}>
                <FormattedMessage id="name" />
              </th>
              <th style={{ padding: "4px 8px", textAlign: "left" }}>
                <FormattedMessage id="resourceType" />
              </th>
              <th style={{ padding: "4px 8px", textAlign: "left" }}>
                <FormattedMessage id="region" />
              </th>
              <th style={{ padding: "4px 8px", textAlign: "left" }}>
                <FormattedMessage id="state" />
              </th>
            </tr>
          </thead>
          <tbody>
            {resources.map((r) => (
              <tr key={r.id} style={{ borderTop: "1px solid rgba(0,0,0,0.08)" }}>
                <td style={{ padding: "4px 8px" }}>{r.name}</td>
                <td style={{ padding: "4px 8px" }}>{r.resource_type}</td>
                <td style={{ padding: "4px 8px" }}>{r.region}</td>
                <td style={{ padding: "4px 8px" }}>
                  <StateLabel stopped_allocated={r.stopped_allocated} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Box>
    </Box>
  );
};

type ByTagsTabProps = {
  onSubmitByTags: () => void;
  isSubmitLoading: boolean;
  onCancel: () => void;
  existingTagSelector?: { tags: Record<string, string>; resource_types?: string[] } | null;
  onRemoveTagFilter?: () => void;
};

const ByTagsTab = ({ onSubmitByTags, isSubmitLoading, onCancel, existingTagSelector, onRemoveTagFilter }: ByTagsTabProps) => {
  const intl = useIntl();
  const { control, setValue, watch } = useFormContext<FormValues>();
  const { fields, append, remove } = useFieldArray({ control, name: FIELD_NAMES.TAG_ENTRIES });

  const allDataSources = useAllDataSources();
  const selectedIds = useWatch({ control, name: FIELD_NAMES.DATA_SOURCES }) ?? [];

  // Check if any selected data source is AWS
  const hasAwsSelected =
    selectedIds.length > 0 &&
    selectedIds.some((id: string) => {
      const ds = allDataSources.find((d) => d.id === id);
      return ds?.type === AWS_CNR;
    });

  const includeEc2 = useWatch({ control, name: FIELD_NAMES.TAG_INCLUDE_EC2 });
  const includeRds = useWatch({ control, name: FIELD_NAMES.TAG_INCLUDE_RDS });
  const tagEntries = useWatch({ control, name: FIELD_NAMES.TAG_ENTRIES });

  const [previewResources, setPreviewResources] = useState<MatchedResource[]>([]);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  const { usePowerByTags } = PowerScheduleService();
  const { onPowerByTags } = usePowerByTags();

  const debouncedTags = useDebouncedValue(tagEntries, { delay: 600 });

  useEffect(() => {
    if (!hasAwsSelected) {
      setPreviewResources([]);
      return;
    }
    const validTags = (debouncedTags ?? []).filter((t: TagEntry) => t.key.trim() && t.value.trim());
    const resourceTypes = [...(includeEc2 ? ["Instance"] : []), ...(includeRds ? ["RDS Instance"] : [])];
    if (!validTags.length || !resourceTypes.length) {
      setPreviewResources([]);
      return;
    }
    const tagsObj = Object.fromEntries(validTags.map(({ key, value }: TagEntry) => [key.trim(), value.trim()]));
    setIsPreviewLoading(true);
    onPowerByTags({ action: "power_on", tags: tagsObj, resource_types: resourceTypes, dry_run: true })
      .then((result) => {
        setPreviewResources((result as { matched_resources: MatchedResource[] }).matched_resources ?? []);
      })
      .catch(() => setPreviewResources([]))
      .finally(() => setIsPreviewLoading(false));
  }, [debouncedTags, includeEc2, includeRds, hasAwsSelected]);

  if (!selectedIds.length) {
    return (
      <Alert severity="info" icon={<InfoOutlinedIcon />} sx={{ mt: 1 }}>
        <FormattedMessage id="selectDataSourceFirst" />
      </Alert>
    );
  }

  if (!hasAwsSelected) {
    return (
      <Alert severity="info" icon={<InfoOutlinedIcon />} sx={{ mt: 1 }}>
        <FormattedMessage id="tagFilterAwsOnly" />
      </Alert>
    );
  }

  return (
    <Stack spacing={SPACING_2}>
      <Box>
        <Typography variant="subtitle2" gutterBottom>
          <FormattedMessage id="resourceTypes" />
        </Typography>
        <FormGroup row>
          <FormControlLabel
            control={
              <Checkbox
                checked={includeEc2 ?? true}
                onChange={(e) => setValue(FIELD_NAMES.TAG_INCLUDE_EC2, e.target.checked)}
                size="small"
              />
            }
            label="EC2"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={includeRds ?? true}
                onChange={(e) => setValue(FIELD_NAMES.TAG_INCLUDE_RDS, e.target.checked)}
                size="small"
              />
            }
            label="RDS / Aurora"
          />
        </FormGroup>
      </Box>
      <Box>
        <Typography variant="subtitle2" gutterBottom>
          <FormattedMessage id="tags" />
        </Typography>
        <Stack spacing={SPACING_1}>
          {fields.map((item, index) => (
            <Box key={item.id} display="flex" gap={SPACING_1} flexWrap="wrap" alignItems="flex-start">
              <Box flexGrow={1} flexBasis="140px">
                <TextInput
                  name={`${FIELD_NAMES.TAG_ENTRIES}.${index}.key`}
                  label={<FormattedMessage id="tagKey" />}
                  required
                  dataTestId={`tag_filter_key_${index}`}
                  validate={{
                    unique: (value, formValues) => {
                      const count = ((formValues as FormValues)[FIELD_NAMES.TAG_ENTRIES] ?? []).filter(
                        (t: TagEntry) => t.key === value,
                      ).length;
                      return count === 1 || intl.formatMessage({ id: "thisFieldMustBeUnique" });
                    },
                  }}
                />
              </Box>
              <Box flexGrow={2} flexBasis="180px">
                <TextInput
                  name={`${FIELD_NAMES.TAG_ENTRIES}.${index}.value`}
                  label={<FormattedMessage id="value" />}
                  required
                  dataTestId={`tag_filter_value_${index}`}
                />
              </Box>
              <Box mt={0.5}>
                <IconButton
                  color="error"
                  icon={<DeleteOutlinedIcon />}
                  onClick={() => remove(index)}
                  tooltip={{ show: true, value: <FormattedMessage id="delete" /> }}
                  dataTestId={`btn_delete_tag_filter_${index}`}
                />
              </Box>
            </Box>
          ))}
          <Box>
            <Button
              dashedBorder
              startIcon={<AddOutlinedIcon />}
              messageId="addTag"
              size="large"
              color="primary"
              onClick={() => append({ key: "", value: "" })}
              dataTestId="btn_add_tag_filter"
            />
          </Box>
        </Stack>
      </Box>
      <PreviewTable resources={previewResources} isLoading={isPreviewLoading} />
      <Box display="flex" gap={1} mt={1} flexWrap="wrap">
        <ButtonLoader
          messageId="saveTagFilter"
          dataTestId="btn_save_tag_filter"
          color="primary"
          variant="contained"
          onClick={onSubmitByTags}
          isLoading={isSubmitLoading}
        />
        <Button messageId="cancel" dataTestId="btn_cancel_tag_filter" onClick={onCancel} />
        {existingTagSelector && onRemoveTagFilter && (
          <Button messageId="removeTagFilter" dataTestId="btn_remove_tag_filter" color="error" onClick={onRemoveTagFilter} />
        )}
      </Box>
    </Stack>
  );
};

export default ByTagsTab;
