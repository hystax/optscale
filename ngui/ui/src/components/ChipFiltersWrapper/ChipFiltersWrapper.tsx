import Chip from "components/Chip";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { isEmpty } from "utils/arrays";
import useStyles from "./ChipFiltersWrapper.styles";

const renderButtons = (buttonsDefinition) =>
  buttonsDefinition.map(({ component: Component, props }) => <Component key={props.key} {...props} />);

const ChipFiltersWrapper = ({ chips, buttonsDefinition = [] }) => {
  const { classes } = useStyles();

  return (
    <div className={classes.wrapper}>
      {chips.map(({ messageId, filterValue }) => (
        <Chip
          key={messageId}
          color="info"
          label={<KeyValueLabel key={messageId} value={filterValue} keyMessageId={messageId} />}
          variant="outlined"
          size="medium"
        />
      ))}
      {!isEmpty(buttonsDefinition) ? renderButtons(buttonsDefinition) : null}
    </div>
  );
};

export default ChipFiltersWrapper;
