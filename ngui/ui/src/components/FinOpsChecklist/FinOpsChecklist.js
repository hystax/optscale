import React, { useEffect, useRef, useState } from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import analyzeCostAnomaliesInCostExplorer from "assets/finops/analyzeCostAnomaliesInCostExplorer.svg";
import connectSlackToReceiveInstantAlerts from "assets/finops/connectSlackToReceiveInstantAlerts.svg";
import createAutoAssignmentRules from "assets/finops/createAutoAssignmentRules.svg";
import createPoolsForAllTheDepartments from "assets/finops/createPoolsForAllTheDepartments.svg";
import inviteTeammates from "assets/finops/inviteTeammates.svg";
import setTTLRulesForAllTheResources from "assets/finops/setTTLRulesForAllTheResources.svg";
import tagAllTheResources from "assets/finops/tagAllTheResources.svg";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import { useIsAllowed } from "hooks/useAllowedActions";
import { SPACING_4, SPACING_6 } from "utils/layouts";
import AdoptionScore from "./AdoptionScore";
import ChecklistCard from "./ChecklistCard";

const FinOpsChecklist = ({ items, update, isLoading = false }) => {
  // show adoption score preloader only at first load
  const isInitialLoad = useRef(true);
  const [showAdoptionScoreLoader, setShowAdoptionScoreLoader] = useState(isInitialLoad.current);
  useEffect(() => {
    isInitialLoad.current = isInitialLoad.current && isLoading;
    setShowAdoptionScoreLoader(isInitialLoad.current);
  }, [isInitialLoad, isLoading]);

  const canUpdate = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const renderChecklistCard = ({ id, titleId, descriptionId, checked }, index) => {
    const image = {
      1: analyzeCostAnomaliesInCostExplorer,
      3: connectSlackToReceiveInstantAlerts,
      4: createAutoAssignmentRules,
      5: createPoolsForAllTheDepartments,
      6: inviteTeammates,
      7: setTTLRulesForAllTheResources,
      8: tagAllTheResources
    }[id];

    return (
      <ChecklistCard
        canUpdate={canUpdate}
        onClick={() => update(id)}
        update={update}
        title={<FormattedMessage id={titleId} />}
        description={
          <FormattedMessage
            id={descriptionId}
            values={{
              link: ([linkDescription]) => {
                const [href, text] = linkDescription.split("|");
                return (
                  <Link href={href} target="_blank" rel="noopener">
                    {text}
                  </Link>
                );
              }
            }}
          />
        }
        checked={checked}
        dataTestId={`p_checkbox_item_${index}`}
        image={image}
      />
    );
  };

  const renderChecklist = () => (
    <Grid container spacing={SPACING_6} justifyContent="center">
      {items.map((item, index) => (
        <Grid item key={item.id} xl={3} lg={4} md={4} sm={6} xs={12}>
          <ContentBackdropLoader isLoading={isLoading}>{renderChecklistCard(item, index)}</ContentBackdropLoader>
        </Grid>
      ))}
    </Grid>
  );

  const checkedNumber = items.filter(({ checked }) => checked).length; // count by bool prop for short lists
  const total = items.length;
  const fraction = checkedNumber / total || 0;

  return (
    <Grid container spacing={SPACING_4} justifyContent="center">
      <Grid item xs={12}>
        <Box display="flex" justifyContent="center">
          <AdoptionScore fraction={fraction} isLoading={showAdoptionScoreLoader} />
        </Box>
      </Grid>
      <Grid item xs={12}>
        <Typography data-test-id="p_finops_description">
          <FormattedMessage id={canUpdate ? "checklist.managerPageDescription" : "checklist.notManagerPageDescription"} />
        </Typography>
      </Grid>
      <Grid item lg={10}>
        {renderChecklist()}
      </Grid>
    </Grid>
  );
};

FinOpsChecklist.propTypes = {
  items: PropTypes.array.isRequired,
  update: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default FinOpsChecklist;
