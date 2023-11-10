import { useState } from "react";
import { Link, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Button from "components/Button";
import Chip from "components/Chip";
import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import ResourcesPerspectiveValuesDescription from "components/ResourcesPerspectiveValuesDescription";
import { RESOURCE_PERSPECTIVES } from "urls";
import { SPACING_1, SPACING_2 } from "utils/layouts";
import useStyles from "./ApplyResourcePerspective.styles";

const ApplyResourcePerspective = ({ perspectives, appliedPerspectiveName, onApply, onCancel }) => {
  const { classes } = useStyles();

  const [selectedPerspectiveName, setSelectedPerspectiveName] = useState(appliedPerspectiveName);

  const selectedPerspectiveData = perspectives[selectedPerspectiveName];

  const renderSelectedPerspectiveValuesDescription = () => {
    const {
      breakdownBy,
      breakdownData,
      filters: { filterValues, appliedFilters }
    } = selectedPerspectiveData;

    const filters = new Filters({
      filters: RESOURCE_FILTERS,
      filterValues,
      appliedFilters
    });

    return (
      <ResourcesPerspectiveValuesDescription
        breakdownBy={breakdownBy}
        breakdownData={breakdownData}
        filters={filters.getAppliedValues()}
      />
    );
  };

  return (
    <Stack spacing={SPACING_2}>
      <Typography>
        <FormattedMessage
          id="selectAndApplyPerspective"
          values={{
            seeAllPerspectivesLink: (
              <Link to={RESOURCE_PERSPECTIVES} component={RouterLink}>
                <FormattedMessage id="seeAllPerspectives" />
              </Link>
            )
          }}
        />
      </Typography>
      <Stack spacing={SPACING_1}>
        <div className={classes.wrapper}>
          {Object.keys(perspectives).map((perspectiveName) => (
            <Chip
              key={perspectiveName}
              variant={selectedPerspectiveName === perspectiveName ? "filled" : "outlined"}
              size="medium"
              onClick={() => setSelectedPerspectiveName(perspectiveName)}
              color={selectedPerspectiveName === perspectiveName ? "secondary" : "info"}
              label={perspectiveName}
            />
          ))}
        </div>
        {selectedPerspectiveName && renderSelectedPerspectiveValuesDescription()}
      </Stack>
      <FormButtonsWrapper>
        <Button
          messageId="apply"
          color="primary"
          variant="contained"
          disabled={!selectedPerspectiveName}
          onClick={() => {
            onApply(selectedPerspectiveName);
            onCancel();
          }}
          dataTestId="btn_apply"
        />
        <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
      </FormButtonsWrapper>
    </Stack>
  );
};

export default ApplyResourcePerspective;
