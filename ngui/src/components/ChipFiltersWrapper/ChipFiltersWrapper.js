import React from "react";
import PropTypes from "prop-types";
import Chip from "components/Chip";
import KeyValueLabel from "components/KeyValueLabel";
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
          label={<KeyValueLabel key={messageId} value={filterValue} messageId={messageId} />}
          variant="outlined"
          size="medium"
        />
      ))}
      {!isEmpty(buttonsDefinition) ? renderButtons(buttonsDefinition) : null}
    </div>
  );
};

ChipFiltersWrapper.propTypes = {
  chips: PropTypes.arrayOf(
    PropTypes.shape({
      messageId: PropTypes.string.isRequired,
      filterValue: PropTypes.any.isRequired
    })
  ).isRequired,
  buttonsDefinition: PropTypes.arrayOf(
    PropTypes.shape({
      component: PropTypes.elementType.isRequired,
      props: PropTypes.shape({
        key: PropTypes.any.isRequired
      })
    })
  )
};

export default ChipFiltersWrapper;
