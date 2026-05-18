import { useEffect, useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box, Checkbox, CircularProgress, FormControlLabel, FormGroup, Stack, Typography } from "@mui/material";
import { FormProvider, useForm, useFieldArray, useFormContext, useWatch } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { RadioGroup, TextInput } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import { useDebouncedValue } from "hooks/useDebouncedValue";
import PowerScheduleService from "services/PowerScheduleService";
import { SPACING_1, SPACING_2 } from "utils/layouts";

type TagEntry = { key: string; value: string };

type MatchedResource = {
  id: string;
  name: string;
  resource_type: string;
  cloud_resource_id: string;
  region: string;
  stopped_allocated: boolean | null;
};

type FormValues = {
  action: "power_on" | "power_off";
  tags: TagEntry[];
  includeEc2: boolean;
  includeRds: boolean;
};

const TagsFields = () => {
  const intl = useIntl();
  const { control } = useFormContext<FormValues>();
  const { fields, append, remove } = useFieldArray({ control, name: "tags" });

  return (
    <Stack spacing={SPACING_1}>
      {fields.map((item, index) => (
        <Box key={item.id} display="flex" gap={SPACING_1} flexWrap="wrap" alignItems="flex-start">
          <Box flexGrow={1} flexBasis="150px">
            <TextInput
              name={`tags.${index}.key`}
              label={<FormattedMessage id="tagKey" />}
              required
              dataTestId={`tag_key_${index}`}
              validate={{
                unique: (value, formValues) => {
                  const count = (formValues.tags as TagEntry[]).filter((t) => t.key === value).length;
                  return count === 1 || intl.formatMessage({ id: "thisFieldMustBeUnique" });
                },
              }}
            />
          </Box>
          <Box flexGrow={2} flexBasis="200px">
            <TextInput
              name={`tags.${index}.value`}
              label={<FormattedMessage id="value" />}
              required
              dataTestId={`tag_value_${index}`}
            />
          </Box>
          <Box mt={0.5}>
            <IconButton
              color="error"
              icon={<DeleteOutlinedIcon />}
              onClick={() => remove(index)}
              tooltip={{ show: true, value: <FormattedMessage id="delete" /> }}
              dataTestId={`btn_delete_tag_${index}`}
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
          dataTestId="btn_add_tag"
        />
      </Box>
    </Stack>
  );
};

const StateLabel = ({ stopped_allocated }: { stopped_allocated: boolean | null }) => {
  if (stopped_allocated === true) return <FormattedMessage id="stopped" />;
  if (stopped_allocated === false) return <FormattedMessage id="running" />;
  return <FormattedMessage id="unknown" />;
};

const PreviewTable = ({ resources, isLoading }: { resources: MatchedResource[]; isLoading: boolean }) => {
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={2}>
        <CircularProgress size={24} />
      </Box>
    );
  }
  if (!resources.length) return null;

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        <FormattedMessage id="matchingResources" values={{ count: resources.length }} />
      </Typography>
      <Box sx={{ maxHeight: 260, overflowY: "auto", border: "1px solid", borderColor: "divider", borderRadius: 1 }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "rgba(0,0,0,0.04)" }}>
              <th style={{ padding: "6px 10px", textAlign: "left" }}>
                <FormattedMessage id="name" />
              </th>
              <th style={{ padding: "6px 10px", textAlign: "left" }}>
                <FormattedMessage id="resourceType" />
              </th>
              <th style={{ padding: "6px 10px", textAlign: "left" }}>
                <FormattedMessage id="region" />
              </th>
              <th style={{ padding: "6px 10px", textAlign: "left" }}>
                <FormattedMessage id="state" />
              </th>
            </tr>
          </thead>
          <tbody>
            {resources.map((r) => (
              <tr key={r.id} style={{ borderTop: "1px solid rgba(0,0,0,0.08)" }}>
                <td style={{ padding: "5px 10px" }}>{r.name}</td>
                <td style={{ padding: "5px 10px" }}>{r.resource_type}</td>
                <td style={{ padding: "5px 10px" }}>{r.region}</td>
                <td style={{ padding: "5px 10px" }}>
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

type PowerByTagsContainerProps = {
  handleClose: () => void;
};

const PowerByTagsContainer = ({ handleClose }: PowerByTagsContainerProps) => {
  const { usePowerByTags } = PowerScheduleService();
  const { onPowerByTags, isLoading } = usePowerByTags();

  const [previewResources, setPreviewResources] = useState<MatchedResource[]>([]);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  const methods = useForm<FormValues>({
    defaultValues: {
      action: "power_on",
      tags: [{ key: "", value: "" }],
      includeEc2: true,
      includeRds: true,
    },
  });

  const { handleSubmit, control, watch } = methods;

  const tags = useWatch({ control, name: "tags" });
  const includeEc2 = useWatch({ control, name: "includeEc2" });
  const includeRds = useWatch({ control, name: "includeRds" });

  const debouncedTags = useDebouncedValue(tags, { delay: 600 });

  useEffect(() => {
    const validTags = debouncedTags.filter((t) => t.key.trim() && t.value.trim());
    const resourceTypes = [...(includeEc2 ? ["Instance"] : []), ...(includeRds ? ["RDS Instance"] : [])];
    if (!validTags.length || !resourceTypes.length) {
      setPreviewResources([]);
      return;
    }
    const tagsObj = Object.fromEntries(validTags.map(({ key, value }) => [key.trim(), value.trim()]));
    setIsPreviewLoading(true);
    onPowerByTags({ action: "power_on", tags: tagsObj, resource_types: resourceTypes, dry_run: true })
      .then((result) => {
        setPreviewResources((result as { matched_resources: MatchedResource[] }).matched_resources ?? []);
      })
      .catch(() => setPreviewResources([]))
      .finally(() => setIsPreviewLoading(false));
  }, [debouncedTags, includeEc2, includeRds]);

  const onSubmit = (formData: FormValues) => {
    const validTags = formData.tags.filter((t) => t.key.trim() && t.value.trim());
    const tags = Object.fromEntries(validTags.map(({ key, value }) => [key.trim(), value.trim()]));
    const resourceTypes = [...(formData.includeEc2 ? ["Instance"] : []), ...(formData.includeRds ? ["RDS Instance"] : [])];
    onPowerByTags({ action: formData.action, tags, resource_types: resourceTypes }).then(() => handleClose());
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack spacing={SPACING_2}>
          <RadioGroup
            name="action"
            labelMessageId="action"
            fullWidth
            row
            radioButtons={[
              { label: <FormattedMessage id="powerOn" />, value: "power_on", dataTestId: "radio_power_on" },
              { label: <FormattedMessage id="powerOff" />, value: "power_off", dataTestId: "radio_power_off" },
            ]}
          />
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              <FormattedMessage id="resourceTypes" />
            </Typography>
            <FormGroup row>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={watch("includeEc2")}
                    onChange={(e) => methods.setValue("includeEc2", e.target.checked)}
                    dataTestId="checkbox_ec2"
                  />
                }
                label="EC2"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={watch("includeRds")}
                    onChange={(e) => methods.setValue("includeRds", e.target.checked)}
                    dataTestId="checkbox_rds"
                  />
                }
                label="RDS / Aurora"
              />
            </FormGroup>
          </Box>
          <TagsFields />
          <PreviewTable resources={previewResources} isLoading={isPreviewLoading} />
        </Stack>
        <FormButtonsWrapper justifyContent="space-between">
          <Box display="flex">
            <ButtonLoader
              messageId="apply"
              dataTestId="btn_apply"
              color="primary"
              variant="contained"
              type="submit"
              isLoading={isLoading}
            />
            <Button messageId="cancel" dataTestId="btn_cancel" onClick={handleClose} />
          </Box>
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export default PowerByTagsContainer;
