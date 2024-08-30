import {
  Box,
  Checkbox,
  FormControl,
  FormControlLabel,
  FormGroup,
  Grid,
  Link,
  Paper,
  Skeleton,
  Typography
} from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import AggregateFunctionFormattedMessage from "components/AggregateFunctionFormattedMessage";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SubTitle from "components/SubTitle";
import TendencyFormattedMessage from "components/TendencyFormattedMessage";
import { ML_TASK_METRICS } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const FIELD_NAME = FIELD_NAMES.METRICS;

const MetricCard = ({ name, metricKey, tendency, aggregateFunction, targetValue, isSelected, onSelect }) => (
  <Paper
    elevation={0}
    sx={{
      // TODO ML: Get the color programmatically?
      // Context: We use the same color as for the input borders
      border: `1px solid #C4C4C4`
    }}
  >
    <Box
      sx={{
        padding: "0px 8px 8px 8px"
      }}
    >
      <div>
        <FormGroup>
          <FormControlLabel control={<Checkbox checked={isSelected} onChange={onSelect} />} label={name} />
        </FormGroup>
      </div>
      <div>
        <KeyValueLabel keyMessageId="key" value={metricKey} />
        <KeyValueLabel keyMessageId="targetValue" value={targetValue} />
        <KeyValueLabel keyMessageId="tendency" value={<TendencyFormattedMessage tendency={tendency} />} />
        <KeyValueLabel
          keyMessageId="aggregateFunction"
          value={<AggregateFunctionFormattedMessage aggregateFunction={aggregateFunction} />}
        />
      </div>
    </Box>
  </Paper>
);

const MetricsField = ({ metrics = [], isLoading = false }) => {
  const { control } = useFormContext<FormValues>();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      render={({ field: { onChange, value } }) =>
        isLoading ? (
          <Skeleton type="rectangular" height={80} />
        ) : (
          <FormControl fullWidth>
            <SubTitle>
              <FormattedMessage id="metrics" />
            </SubTitle>
            {isEmptyArray(metrics) ? (
              <Typography>
                <FormattedMessage
                  id="noMetricsToTrack"
                  values={{
                    link: (chunks) => (
                      <Link data-test-id="link_metrics_library" href={ML_TASK_METRICS} target="_blank" rel="noopener">
                        {chunks}
                      </Link>
                    )
                  }}
                />
              </Typography>
            ) : (
              <>
                <Typography gutterBottom>
                  <FormattedMessage id="createMlTask.selectMetrics" />
                </Typography>
                <Grid container spacing={1}>
                  {metrics.map((metric) => {
                    const isSelected = value.includes(metric.id);
                    const onSelect = () => {
                      if (isSelected) {
                        onChange(value.filter((v) => v !== metric.id));
                      } else {
                        onChange([...value, metric.id]);
                      }
                    };

                    return (
                      <Grid key={metric.name} item xs={6} sm={4} md={6} lg={6} xl={4}>
                        <MetricCard
                          isSelected={isSelected}
                          onSelect={onSelect}
                          name={metric.name}
                          metricKey={metric.key}
                          tendency={metric.tendency}
                          aggregateFunction={metric.func}
                          targetValue={metric.target_value}
                        />
                      </Grid>
                    );
                  })}
                </Grid>
              </>
            )}
          </FormControl>
        )
      }
    />
  );
};

export default MetricsField;
