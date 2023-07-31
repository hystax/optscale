import React from "react";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import { Grid, Paper } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { useNavigate } from "react-router-dom";
import FormattedMoney from "components/FormattedMoney";
import RecommendationLink from "components/RecommendationLink";
import SubTitle from "components/SubTitle";
import TitleValue from "components/TitleValue";
import WrapperCard from "components/WrapperCard";
import {
  CATEGORY_COST,
  CATEGORY_SECURITY
} from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import { RECOMMENDATIONS } from "urls";
import { SPACING_2 } from "utils/layouts";
import useStyles from "./RecommendationsCard.styles";

const InfoCard = ({ title, value, isLoading, dataTestIds = {} }) => {
  const { classes } = useStyles();

  const { title: titleDataTestId, value: valueDataTestId } = dataTestIds;

  const body = (
    <Paper variant="outlined" className={classes.infoCard}>
      <SubTitle data-test-id={titleDataTestId}>{title}</SubTitle>
      <TitleValue dataTestId={valueDataTestId}>{value}</TitleValue>
    </Paper>
  );

  return isLoading ? (
    <Skeleton width="100%" variant="rectangular">
      {body}
    </Skeleton>
  ) : (
    body
  );
};

const RecommendationsCard = ({ isLoading, possibleMonthlySavings, costRecommendationsCount, securityRecommendationsCount }) => {
  const navigate = useNavigate();

  const goToRecommendations = () => navigate(RECOMMENDATIONS);

  return (
    <WrapperCard
      needAlign
      title={<FormattedMessage id="recommendations" />}
      titleButton={{
        type: "icon",
        tooltip: {
          title: <FormattedMessage id="goToRecommendations" />
        },
        buttonProps: {
          icon: <ExitToAppOutlinedIcon />,
          isLoading,
          onClick: goToRecommendations,
          dataTestId: "btn_go_to_recommendations"
        }
      }}
      dataTestIds={{
        wrapper: "block_recommendations",
        title: "lbl_recommendations"
      }}
      elevation={0}
    >
      {
        <Grid container spacing={SPACING_2}>
          <Grid item xs={12}>
            <InfoCard
              title={<FormattedMessage id="possibleMonthlySavings" />}
              value={<FormattedMoney value={possibleMonthlySavings} />}
              isLoading={isLoading}
              dataTestIds={{
                title: "block_recommendations_lbl_savings",
                value: "block_recommendations_lbl_savings_value"
              }}
            />
          </Grid>
          <Grid item xs={6}>
            <InfoCard
              title={
                <RecommendationLink category={CATEGORY_COST} dataTestId="block_recommendations_cost_link">
                  <FormattedMessage id="costOptimizations" />
                </RecommendationLink>
              }
              value={<FormattedNumber value={costRecommendationsCount} />}
              isLoading={isLoading}
              dataTestIds={{
                value: "block_recommendations_cost_value"
              }}
            />
          </Grid>
          <Grid item xs={6}>
            <InfoCard
              title={
                <RecommendationLink category={CATEGORY_SECURITY} dataTestId="block_recommendations_security_link">
                  <FormattedMessage id="security" />
                </RecommendationLink>
              }
              value={<FormattedNumber value={securityRecommendationsCount} />}
              isLoading={isLoading}
              dataTestIds={{
                value: "block_recommendations_security_value"
              }}
            />
          </Grid>
        </Grid>
      }
    </WrapperCard>
  );
};

RecommendationsCard.propTypes = {
  possibleMonthlySavings: PropTypes.number,
  costRecommendationsCount: PropTypes.number,
  securityRecommendationsCount: PropTypes.number,
  isLoading: PropTypes.bool
};

export default RecommendationsCard;
