import { useEffect, useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box, Checkbox, CircularProgress, Collapse, FormControlLabel, FormGroup, Switch, Typography } from "@mui/material";
import { useFieldArray, useFormContext, useWatch } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import { TextInput } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import { useDebouncedValue } from "hooks/useDebouncedValue";
import PowerScheduleService from "services/PowerScheduleService";
import { SPACING_1 } from "utils/layouts";
import type { FormValues, TagEntry } from "../types";

type MatchedResource = {
  id: string;
  name: string;
  resource_type: string;
  region: string;
  stopped_allocated: boolean | null;
};

const StateLabel = ({ stopped_allocated }: { stopped_allocated: boolean | null }) => {
  if (stopped_allocated === true) return <FormattedMessage id="stopped" />;
  if (stopped_allocated === false) return <FormattedMessage id="running" />;
  return <FormattedMessage id="unknown" />;
};

const PreviewTable = ({ resources, isLoading }: { resources: MatchedResource[]; isLoading: boolean }) => {
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={1}>
        <CircularProgress size={20} />
      </Box>
    );
  }
  if (!resources.length) return null;

  return (
    <Box mt={1}>
      <Typography variant="caption" color="text.secondary">
        <FormattedMessage id="matchingResources" values={{ count: resources.length }} />
      </Typography>
      <Box
        sx={{
          maxHeight: 200,
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

const TagSelectorField = ({ isLoading = false }: { isLoading?: boolean }) => {
  const intl = useIntl();
  const { control, setValue } = useFormContext<FormValues>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: "tagSelector.tags",
  });

  const enabled = useWatch({ control, name: "tagSelector.enabled" });
  const includeEc2 = useWatch({ control, name: "tagSelector.includeEc2" });
  const includeRds = useWatch({ control, name: "tagSelector.includeRds" });
  const tags = useWatch({ control, name: "tagSelector.tags" });

  const [previewResources, setPreviewResources] = useState<MatchedResource[]>([]);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  const { usePowerByTags } = PowerScheduleService();
  const { onPowerByTags } = usePowerByTags();

  const debouncedTags = useDebouncedValue(tags, { delay: 600 });

  useEffect(() => {
    if (!enabled) {
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
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedTags, includeEc2, includeRds, enabled]);

  return (
    <Box mt={2}>
      <Box display="flex" alignItems="center" gap={1}>
        <Typography variant="subtitle2">
          <FormattedMessage id="tagBasedResources" />
        </Typography>
        <Switch
          checked={enabled}
          onChange={(e) => setValue("tagSelector.enabled", e.target.checked)}
          size="small"
          disabled={isLoading}
        />
      </Box>
      <Collapse in={enabled}>
        <Box mt={1} pl={1} borderLeft="2px solid" borderColor="divider">
          <Typography variant="caption" color="text.secondary" display="block" mb={1}>
            <FormattedMessage id="tagBasedResourcesHint" />
          </Typography>
          <FormGroup row>
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeEc2 ?? true}
                  onChange={(e) => setValue("tagSelector.includeEc2", e.target.checked)}
                  size="small"
                  disabled={isLoading}
                />
              }
              label="EC2"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeRds ?? true}
                  onChange={(e) => setValue("tagSelector.includeRds", e.target.checked)}
                  size="small"
                  disabled={isLoading}
                />
              }
              label="RDS / Aurora"
            />
          </FormGroup>
          <Box mt={1}>
            <Box display="flex" flexDirection="column" gap={SPACING_1}>
              {fields.map((item, index) => (
                <Box key={item.id} display="flex" gap={SPACING_1} flexWrap="wrap" alignItems="flex-start">
                  <Box flexGrow={1} flexBasis="140px">
                    <TextInput
                      name={`tagSelector.tags.${index}.key`}
                      label={<FormattedMessage id="tagKey" />}
                      required
                      dataTestId={`tag_selector_key_${index}`}
                      disabled={isLoading}
                      validate={{
                        unique: (value, formValues) => {
                          const count = ((formValues.tagSelector as FormValues["tagSelector"])?.tags ?? []).filter(
                            (t: TagEntry) => t.key === value
                          ).length;
                          return count === 1 || intl.formatMessage({ id: "thisFieldMustBeUnique" });
                        },
                      }}
                    />
                  </Box>
                  <Box flexGrow={2} flexBasis="180px">
                    <TextInput
                      name={`tagSelector.tags.${index}.value`}
                      label={<FormattedMessage id="value" />}
                      required
                      dataTestId={`tag_selector_value_${index}`}
                      disabled={isLoading}
                    />
                  </Box>
                  <Box mt={0.5}>
                    <IconButton
                      color="error"
                      icon={<DeleteOutlinedIcon />}
                      onClick={() => remove(index)}
                      tooltip={{ show: true, value: <FormattedMessage id="delete" /> }}
                      dataTestId={`btn_delete_tag_selector_${index}`}
                      disabled={isLoading}
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
                  dataTestId="btn_add_tag_selector"
                  disabled={isLoading}
                />
              </Box>
            </Box>
          </Box>
          <PreviewTable resources={previewResources} isLoading={isPreviewLoading} />
        </Box>
      </Collapse>
    </Box>
  );
};

export default TagSelectorField;
