import ViewColumnIcon from "@mui/icons-material/ViewColumn";
import Checkbox from "@mui/material/Checkbox";
import Divider from "@mui/material/Divider";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import Popover from "components/Popover";
import useStyles from "./ColumnsSelector.styles";

const ColumnsSelector = ({ tableContext, dataTestIds }) => {
  const { classes } = useStyles();

  const isAllVisible = tableContext.getIsAllColumnsVisible();

  const handleToggleAllColumnsVisibility = tableContext.getToggleAllColumnsVisibilityHandler();

  return (
    <Popover
      label={<IconButton icon={<ViewColumnIcon />} dataTestId={dataTestIds.button} />}
      menu={
        <span data-test-id={dataTestIds.container}>
          <MenuItem onClick={handleToggleAllColumnsVisibility} data-test-id={dataTestIds.clear}>
            <Checkbox size="small" checked={isAllVisible} />
            <ListItemText primary={isAllVisible ? <FormattedMessage id="clearAll" /> : <FormattedMessage id="selectAll" />} />
          </MenuItem>
          <Divider />
          <div className={classes.menuItems}>
            {tableContext
              .getAllLeafColumns()
              .filter((column) => column.getCanHide())
              .map((column) => {
                /**
                 * TODO: Find a better name for the "accessor" variable
                 */
                const { accessor, messageId, title, dataTestId } = column.columnDef.columnSelector;

                const getTitle = () => {
                  if (messageId) {
                    return <FormattedMessage id={messageId} />;
                  }
                  return title ?? accessor;
                };

                return (
                  <MenuItem
                    // TODO: value is not necessary, accessor as a key is confusing, it duplicates messageId in most cases
                    key={accessor}
                    value={accessor}
                    className={classes.menuItem}
                    onClick={column.getToggleVisibilityHandler()}
                    data-test-id={dataTestId}
                  >
                    <Checkbox size="small" checked={column.getIsVisible()} />
                    <ListItemText primary={getTitle()} />
                  </MenuItem>
                );
              })}
          </div>
        </span>
      }
    />
  );
};

export default ColumnsSelector;
