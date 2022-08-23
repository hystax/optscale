import React from "react";
import ViewColumnIcon from "@mui/icons-material/ViewColumn";
import Checkbox from "@mui/material/Checkbox";
import Divider from "@mui/material/Divider";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import IconButton from "components/IconButton";
import Popover from "components/Popover";
import { useRootData } from "hooks/useRootData";
import { saveHiddenColumns, COLUMNS } from "reducers/columns";
import useStyles from "./styles/ColumnsSelector.styles";

const ColumnsSelector = ({ columnsSelectorUID, hideableColumns, setHiddenColumns, dataTestIds }) => {
  const { classes } = useStyles();
  const dispatch = useDispatch();

  const { rootData: savedHiddenColumns = [] } = useRootData(COLUMNS, (result) => result?.[columnsSelectorUID]);

  const columnIsStatic = (columnAccessor) => !hideableColumns.find(({ accessor }) => accessor === columnAccessor);

  // if all columns in redux are static
  const allVisible = savedHiddenColumns.reduce((accum, column) => accum && columnIsStatic(column), true);

  const handleItemClick = (columnAccessor) => {
    // only not static columns
    const savedHideableColumns = savedHiddenColumns.filter((column) => !columnIsStatic(column));

    let hiddenColumnsUpdated;
    if (savedHideableColumns.indexOf(columnAccessor) === -1) {
      hiddenColumnsUpdated = savedHideableColumns.concat(columnAccessor);
    } else {
      hiddenColumnsUpdated = savedHideableColumns.filter((c) => c !== columnAccessor);
    }

    setHiddenColumns(hiddenColumnsUpdated); // table state
    dispatch(saveHiddenColumns(columnsSelectorUID, hiddenColumnsUpdated)); // redux save
  };

  const handleSelectAll = () => {
    const hiddenColumnsUpdated = allVisible ? hideableColumns.map(({ accessor }) => accessor) : [];
    setHiddenColumns(hiddenColumnsUpdated);
    dispatch(saveHiddenColumns(columnsSelectorUID, hiddenColumnsUpdated));
  };

  return (
    <Popover
      label={<IconButton icon={<ViewColumnIcon />} dataTestId={dataTestIds.button} />}
      menu={
        <span data-test-id={dataTestIds.container}>
          <MenuItem onClick={handleSelectAll} data-test-id={dataTestIds.clear}>
            <Checkbox size="small" checked={allVisible} />
            <ListItemText primary={allVisible ? <FormattedMessage id="clearAll" /> : <FormattedMessage id="selectAll" />} />
          </MenuItem>
          <Divider />
          <div className={classes.menuItems}>
            {hideableColumns.map(({ accessor, title, dataTestId = null }) => (
              <MenuItem
                key={accessor}
                value={title}
                className={classes.menuItem}
                onClick={() => handleItemClick(accessor)}
                data-test-id={dataTestId}
              >
                <Checkbox size="small" checked={savedHiddenColumns.indexOf(accessor) === -1} />
                <ListItemText primary={title} />
              </MenuItem>
            ))}
          </div>
        </span>
      }
    />
  );
};

export const ColumnsSelectorTestIdsProp = PropTypes.shape({
  container: PropTypes.string,
  button: PropTypes.string,
  clear: PropTypes.string
});

export const ColumnsSelectorProps = {
  columnsSelectorUID: PropTypes.string,
  hideableColumns: PropTypes.arrayOf(
    PropTypes.shape({
      accessor: PropTypes.string,
      title: PropTypes.node,
      dataTestId: PropTypes.string
    })
  ),
  setHiddenColumns: PropTypes.func,
  dataTestIds: ColumnsSelectorTestIdsProp
};

ColumnsSelector.propTypes = ColumnsSelectorProps;

export default ColumnsSelector;
