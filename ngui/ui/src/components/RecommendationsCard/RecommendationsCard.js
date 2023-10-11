import React from "react";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import GppGoodOutlinedIcon from "@mui/icons-material/GppGoodOutlined";
import GppMaybeOutlinedIcon from "@mui/icons-material/GppMaybeOutlined";
import MonetizationOnOutlinedIcon from "@mui/icons-material/MonetizationOnOutlined";
import { Grid } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { createSearchParams, useNavigate } from "react-router-dom";
import RecommendationLink from "components/RecommendationLink";
import WrapperCard from "components/WrapperCard";
import {
  CATEGORY_ALL,
  CATEGORY_COST,
  CATEGORY_CRITICAL,
  CATEGORY_SECURITY
} from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import { ALL_SERVICES } from "hooks/useRecommendationServices";
import { RECOMMENDATIONS, RECOMMENDATION_CATEGORY_QUERY_PARAMETER, RECOMMENDATION_SERVICE_QUERY_PARAMETER } from "urls";
import { SPACING_2 } from "utils/layouts";
import { InfoCard, PossibleSavingsCard } from "./Components";

const RecommendationsCard = ({
  isLoading,
  possibleMonthlySavings,
  costRecommendationsCount,
  securityRecommendationsCount,
  criticalRecommendationsCount,
  thisMonthExpensesForecast
}) => {
  const navigate = useNavigate();

  const seeAllRecommendations = () =>
    navigate({
      pathname: RECOMMENDATIONS,
      search: `?${createSearchParams({
        [RECOMMENDATION_CATEGORY_QUERY_PARAMETER]: CATEGORY_ALL,
        [RECOMMENDATION_SERVICE_QUERY_PARAMETER]: CATEGORY_ALL
      })}`
    });

  return (
    <WrapperCard
      needAlign
      title={<FormattedMessage id="recommendations" />}
      titleButton={{
        type: "icon",
        tooltip: {
          title: <FormattedMessage id="seeAllRecommendations" />
        },
        buttonProps: {
          icon: <ExitToAppOutlinedIcon />,
          isLoading,
          onClick: seeAllRecommendations,
          dataTestId: "btn_see_all_recommendations"
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
            <PossibleSavingsCard
              isLoading={isLoading}
              possibleMonthlySavings={possibleMonthlySavings}
              thisMonthExpensesForecast={thisMonthExpensesForecast}
            />
          </Grid>
          <Grid item xs={12} lg={4}>
            <InfoCard
              title={
                <RecommendationLink
                  category={CATEGORY_COST}
                  service={ALL_SERVICES}
                  dataTestId="block_recommendations_cost_link"
                >
                  <FormattedMessage id="cost" />
                </RecommendationLink>
              }
              color="success"
              icon={<MonetizationOnOutlinedIcon />}
              value={<FormattedNumber value={costRecommendationsCount} />}
              isLoading={isLoading}
              dataTestIds={{
                value: "block_recommendations_cost_value"
              }}
            />
          </Grid>
          <Grid item xs={12} lg={4}>
            <InfoCard
              title={
                <RecommendationLink
                  category={CATEGORY_SECURITY}
                  service={ALL_SERVICES}
                  dataTestId="block_recommendations_security_link"
                >
                  <FormattedMessage id="security" />
                </RecommendationLink>
              }
              color="warning"
              icon={<GppGoodOutlinedIcon />}
              value={<FormattedNumber value={securityRecommendationsCount} />}
              isLoading={isLoading}
              dataTestIds={{
                value: "block_recommendations_security_value"
              }}
            />
          </Grid>
          <Grid item xs={12} lg={4}>
            <InfoCard
              title={
                <RecommendationLink
                  category={CATEGORY_CRITICAL}
                  service={ALL_SERVICES}
                  dataTestId="block_recommendations_critical_link"
                >
                  <FormattedMessage id="critical" />
                </RecommendationLink>
              }
              color="error"
              icon={<GppMaybeOutlinedIcon />}
              value={<FormattedNumber value={criticalRecommendationsCount} />}
              isLoading={isLoading}
              dataTestIds={{
                value: "block_recommendations_critical_value"
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
  criticalRecommendationsCount: PropTypes.number,
  archivedRecommendationsCount: PropTypes.number,
  thisMonthExpensesForecast: PropTypes.number,
  isLoading: PropTypes.bool
};

export default RecommendationsCard;
