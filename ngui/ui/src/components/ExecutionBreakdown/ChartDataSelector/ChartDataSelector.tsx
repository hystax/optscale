import { Autocomplete } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import Chip from "components/Chip";
import CircleLabel from "components/CircleLabel";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { SPACING_2 } from "utils/layouts";

const ChartDataSelector = ({ selectedBreakdowns, colorsMap, breakdownConfig, onChange, isLoading = false }) => {
  const theme = useTheme();
  const breakdownsColored = breakdownConfig
    .map((item) => ({
      color: colorsMap[item.name] || theme.palette.common.black,
      ...item
    }))
    .sort(({ isNotImplemented: a = false }, { isNotImplemented: b = false }) => a - b);

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <Autocomplete
      sx={{ mt: SPACING_2 }}
      value={breakdownsColored.filter(({ name }) => selectedBreakdowns.includes(name))}
      multiple
      disableClearable
      clearOnBlur
      onChange={(event, newValue) => {
        onChange(newValue.map(({ name }) => name));
      }}
      options={breakdownsColored}
      getOptionDisabled={({ isNotImplemented }) => isNotImplemented}
      isOptionEqualToValue={(option, value) => option.name === value.name}
      getOptionLabel={({ renderBreakdownName }) => renderBreakdownName()}
      renderOption={(props, { name, renderBreakdownName, color, isNotImplemented }) => (
        <li {...props} key={name}>
          <CircleLabel
            label={
              <>
                {renderBreakdownName()}
                {isNotImplemented && (
                  <>
                    &nbsp;— <FormattedMessage id="comingSoon" />
                  </>
                )}
              </>
            }
            figureColor={color}
            textFirst={false}
          />
        </li>
      )}
      renderTags={(value, getTagProps) =>
        value.map((option, index) => (
          <Chip
            key={option.name}
            variant="outlined"
            color="info"
            label={<CircleLabel label={option.renderBreakdownName()} figureColor={option.color} textFirst={false} />}
            {...getTagProps({ index })}
          />
        ))
      }
      renderInput={(params) => <Input {...params} dataTestId="input_chart_selector" label={<FormattedMessage id="data" />} />}
    />
  );
};

export default ChartDataSelector;
