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
import KeyValueLabel from "components/KeyValueLabel";
import SubTitle from "components/SubTitle";
import TendencyFormattedMessage from "components/TendencyFormattedMessage";
import { ML_MODELS_PARAMETERS } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";

const Parameter = ({ name, goalKey, tendency, aggregateFunction, value, isSelected, onSelect }) => (
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
        <KeyValueLabel messageId="key" value={goalKey} />
        <KeyValueLabel messageId="goalValue" value={value} />
        <KeyValueLabel messageId="tendency" value={<TendencyFormattedMessage tendency={tendency} />} />
        <KeyValueLabel
          messageId="aggregateFunction"
          value={<AggregateFunctionFormattedMessage aggregateFunction={aggregateFunction} />}
        />
      </div>
    </Box>
  </Paper>
);

const MlModelCreateFormParametersField = ({ name, parameters = [], isLoading = false }) => {
  const { control } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field: { onChange, value } }) =>
        isLoading ? (
          <Skeleton type="rectangular" height={80} />
        ) : (
          <FormControl fullWidth>
            <SubTitle>
              <FormattedMessage id="parameters" />
            </SubTitle>
            {isEmptyArray(parameters) ? (
              <Typography>
                <FormattedMessage
                  id="noParametersToTrack"
                  values={{
                    link: (chunks) => (
                      <Link data-test-id="link_parameters_library" href={ML_MODELS_PARAMETERS} target="_blank" rel="noopener">
                        {chunks}
                      </Link>
                    )
                  }}
                />
              </Typography>
            ) : (
              <>
                <Typography gutterBottom>
                  <FormattedMessage id="createMlModel.selectParameters" />
                </Typography>
                <Grid container spacing={1}>
                  {parameters.map((parameter) => {
                    const isSelected = value.includes(parameter.id);
                    const onSelect = () => {
                      if (isSelected) {
                        onChange(value.filter((v) => v !== parameter.id));
                      } else {
                        onChange([...value, parameter.id]);
                      }
                    };

                    return (
                      <Grid key={parameter.name} item xs={6} sm={4} md={6} lg={6} xl={4}>
                        <Parameter
                          isSelected={isSelected}
                          onSelect={onSelect}
                          name={parameter.name}
                          goalKey={parameter.key}
                          tendency={parameter.tendency}
                          aggregateFunction={parameter.func}
                          value={parameter.target_value}
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

export default MlModelCreateFormParametersField;
