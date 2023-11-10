import { useEffect, useRef, useState } from "react";
import { Box, Checkbox, FormHelperText, FormControl, InputLabel, MenuItem, OutlinedInput, Select } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Chip from "components/Chip";
import CloudLabel from "components/CloudLabel";
import useStyles from "./DataSourceMultiSelect.styles";

const DataSourceMultiSelect = ({
  dataSourceIds,
  allDataSources,
  onChange,
  displayEmpty = false,
  fullWidth = false,
  required = false,
  error,
  helperText,
  name,
  onBlur,
  inputRef
}) => {
  const handleChange = (event) => {
    const {
      target: { value }
    } = event;

    onChange(
      // On autofill we get a stringified value. See mui docs:
      // https://mui.com/material-ui/react-select/#checkmarks
      typeof value === "string" ? value.split(",") : value
    );
  };

  const handleDeleteChip = (deletedDataSourceId) => {
    onChange(dataSourceIds.filter((id) => id !== deletedDataSourceId));
  };

  const { classes } = useStyles();

  const dataSourcesMessage = <FormattedMessage id="dataSources" />;

  const selectRef = useRef(null);

  /**
   * The Mui selector currently calculates the popover width only when
   * the menu is update (e.g closed or opened).
   *
   * However, because we have a varying number of selected items, the width of the input
   * increases while the menu width remains static.
   *
   * As a result, we need to implement a handler or listener to update the
   * menu width whenever the selected data changes.
   *
   * https://github.com/mui/material-ui/blob/master/packages/mui-material/src/Select/SelectInput.js#L463
   */
  const [menuPaperMinWidth, setMenuPaperMinWidth] = useState(0);

  useEffect(() => {
    setMenuPaperMinWidth(selectRef?.current?.clientWidth ?? 0);
  }, [dataSourceIds]);

  return (
    <FormControl className={classes.formControl} fullWidth={fullWidth}>
      <InputLabel shrink={displayEmpty ? true : undefined} required={required} id="select-data-source-label" error={error}>
        {dataSourcesMessage}
      </InputLabel>
      <Select
        ref={selectRef}
        name={name}
        labelId="select-data-source-label"
        id="select-data-source"
        multiple
        displayEmpty={displayEmpty}
        onBlur={onBlur}
        inputRef={inputRef}
        value={dataSourceIds}
        onChange={handleChange}
        MenuProps={{
          PaperProps: {
            style: {
              minWidth: menuPaperMinWidth
            }
          },
          anchorOrigin: {
            vertical: "bottom",
            horizontal: "left"
          },
          transformOrigin: {
            vertical: "top",
            horizontal: "left"
          }
        }}
        error={error}
        input={<OutlinedInput notched={displayEmpty ? true : undefined} label={dataSourcesMessage} />}
        renderValue={(selected) => {
          if (selected.length === 0) {
            return <FormattedMessage id="all" />;
          }

          const selectedDataSourcesChips = allDataSources
            .map(({ name: dataSourceName, id, type }) => {
              if (selected.indexOf(id) > -1) {
                return (
                  <Chip
                    key={id}
                    size="small"
                    label={<CloudLabel name={dataSourceName} type={type} disableLink />}
                    variant="outlined"
                    stopMouseDownPropagationOnDelete
                    onDelete={() => handleDeleteChip(id)}
                  />
                );
              }

              return false;
            })
            .filter(Boolean);
          return <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>{selectedDataSourcesChips}</Box>;
        }}
      >
        {allDataSources.map(({ name: dataSourceName, id, type }) => (
          <MenuItem key={dataSourceName} value={id} className={classes.menuItem}>
            <Checkbox checked={dataSourceIds.indexOf(id) > -1} className={classes.checkbox} />
            <CloudLabel key={id} name={dataSourceName} type={type} disableLink />
          </MenuItem>
        ))}
      </Select>
      {error && <FormHelperText error>{helperText}</FormHelperText>}
    </FormControl>
  );
};

export default DataSourceMultiSelect;
