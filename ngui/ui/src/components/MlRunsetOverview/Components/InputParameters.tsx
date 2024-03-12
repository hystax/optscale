import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import CodeEditor from "components/CodeEditor";
import FormattedDuration from "components/FormattedDuration";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import QuestionMark from "components/QuestionMark";
import SummaryList from "components/SummaryList";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ML_RUNSET_ABORT_CONDITION_TYPES } from "utils/constants";

const InputParameters = ({ runset, isLoading }) => {
  const { isDemo } = useOrganizationInfo();

  const {
    cloud_account: { id: dataSourceId, name: dataSourceName, type: dataSourceType, deleted: isDataSourceDeleted = false } = {},
    region: { name: regionName, cloud_type: regionDataSourceType } = {},
    instance_size: { name: instanceSizeName, cloud_type: instanceSizeDataSourceType } = {},
    max_parallel_runs: maximumParallelRuns,
    hyperparameters = {},
    destroy_conditions: abortConditions = {},
    commands,
    spot_settings: spotSettings
  } = runset;

  return (
    <Box display="flex" flexWrap="wrap" rowGap={1} columnGap={16}>
      <Box>
        <SummaryList
          titleMessage={<FormattedMessage id="details" />}
          isLoading={isLoading}
          items={
            <>
              <KeyValueLabel
                keyMessageId="dataSource"
                value={
                  <CloudLabel
                    id={dataSourceId}
                    name={dataSourceName}
                    type={dataSourceType}
                    disableLink={isDemo || isDataSourceDeleted}
                  />
                }
                dataTestIds={{ key: "p_data_source_key", value: "p_data_source_value" }}
              />
              <KeyValueLabel
                keyMessageId="region"
                value={<CloudLabel name={regionName} type={regionDataSourceType} disableLink />}
                dataTestIds={{ key: "p_region_key", value: "p_region_value" }}
              />
              <KeyValueLabel
                keyMessageId="instanceSize"
                value={<CloudLabel name={instanceSizeName} type={instanceSizeDataSourceType} disableLink />}
                dataTestIds={{ key: "p_instance_size_key", value: "p_instance_size_value" }}
              />
              <KeyValueLabel
                keyMessageId="maximumParallelRuns"
                value={maximumParallelRuns}
                dataTestIds={{ key: "p_maximum_parallel_runs_key", value: "p_maximum_parallel_runs_value" }}
              />
              {spotSettings && (
                <KeyValueLabel
                  keyMessageId="spotInstances"
                  value={
                    <Box display="flex" alignItems="center">
                      <span>
                        <FormattedMessage
                          id="xAttemptsBeforePayAsYouGo"
                          values={{
                            value: spotSettings.tries,
                            strong: (chunks) => <strong>{chunks}</strong>
                          }}
                        />
                      </span>
                      <QuestionMark messageId="xAttemptsBeforePayAsYouGoDescription" fontSize="small" Icon={InfoOutlinedIcon} />
                    </Box>
                  }
                  isBoldValue={false}
                  dataTestIds={{ key: "p_using_spot_instances_key", value: "p_using_spot_instances_value" }}
                />
              )}
            </>
          }
        />
      </Box>
      <Box>
        <SummaryList
          titleMessage={<FormattedMessage id="hyperparametersCount" />}
          isLoading={isLoading}
          items={Object.entries(hyperparameters).map(([hyperparameterName, hyperparameterValues]) => {
            const values = hyperparameterValues.split(",");

            return (
              <KeyValueLabel
                key={hyperparameterName}
                keyText={hyperparameterName}
                value={
                  <Box display="flex" alignItems="center">
                    <span>{values.length}</span>
                    <QuestionMark
                      tooltipText={values.map((value) => (
                        <div key={value}>{value}</div>
                      ))}
                      fontSize="small"
                      Icon={InfoOutlinedIcon}
                    />
                  </Box>
                }
              />
            );
          })}
        />
      </Box>
      <Box>
        <SummaryList
          titleMessage={<FormattedMessage id="stopConditions" />}
          isLoading={isLoading}
          items={Object.entries(abortConditions).map(([conditionName, conditionValue]) => {
            const getConditionLabel = () => {
              if (conditionName === ML_RUNSET_ABORT_CONDITION_TYPES.MAX_BUDGET) {
                return (
                  <FormattedMessage id="maxBudgetStopCondition" values={{ value: <FormattedMoney value={conditionValue} /> }} />
                );
              }
              if (conditionName === ML_RUNSET_ABORT_CONDITION_TYPES.REACHED_GOALS) {
                return conditionValue === true ? <FormattedMessage id="abortRunsetWhenOneOfRunsReachesModelGoals" /> : null;
              }
              if (conditionName === ML_RUNSET_ABORT_CONDITION_TYPES.MAX_DURATION) {
                return (
                  <FormattedMessage
                    id="maxDurationStopCondition"
                    values={{ value: <FormattedDuration durationInSeconds={conditionValue} /> }}
                  />
                );
              }
              return null;
            };

            const conditionLabel = getConditionLabel();

            return conditionLabel ? <Typography key={conditionName}>{conditionLabel}</Typography> : null;
          })}
        />
      </Box>
      <Box>
        <SummaryList
          titleMessage={<FormattedMessage id="commandsToExecute" />}
          isLoading={isLoading}
          items={
            commands ? (
              <CodeEditor
                value={commands}
                language="bash"
                style={{
                  /**
                   * The code block height has been limited to 95px,
                   * which is an empirical value chosen to accommodate four rows of code.
                   */
                  overflowY: "auto",
                  height: "95px"
                }}
                readOnly
              />
            ) : (
              <Typography>
                <FormattedMessage id="none" />
              </Typography>
            )
          }
        />
      </Box>
    </Box>
  );
};

export default InputParameters;
