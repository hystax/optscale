import { useEffect, useMemo } from "react";
import { Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { getArchivedOptimizationDetails } from "api";
import { GET_ARCHIVED_OPTIMIZATION_DETAILS } from "api/restapi/actionTypes";
import Accordion from "components/Accordion";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import RecommendationAccordionTitle from "components/RecommendationAccordionTitle";
import RecommendationDescription from "components/RecommendationDescription";
import RecommendationLimitWarning from "components/RecommendationLimitWarning";
import Table from "components/Table";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import {
  ARCHIVATION_REASON_DESCRIPTION_MESSAGE_ID,
  ARCHIVATION_REASON_MESSAGE_ID,
  RECOMMENDATIONS_LIMIT_FILTER
} from "utils/constants";
import { EN_FULL_FORMAT, formatUTC } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";

const ArchivedRecommendationAccordion = ({
  recommendationType,
  count,
  reason,
  archivedAt,
  onChange,
  isExpanded = false,
  dataTestId
}) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { items = [], limit }
  } = useApiData(GET_ARCHIVED_OPTIMIZATION_DETAILS, {});

  const { isLoading, shouldInvoke } = useApiState(GET_ARCHIVED_OPTIMIZATION_DETAILS, {
    organizationId,
    type: recommendationType,
    archivedAt,
    reason
  });

  const allRecommendations = useAllRecommendations();

  useEffect(() => {
    if (isExpanded && shouldInvoke) {
      dispatch(
        getArchivedOptimizationDetails(organizationId, {
          type: recommendationType,
          archivedAt,
          reason,
          limit: RECOMMENDATIONS_LIMIT_FILTER
        })
      );
    }
  }, [archivedAt, dispatch, isExpanded, recommendationType, organizationId, reason, shouldInvoke]);

  const { columns, title } = useMemo(
    () => new allRecommendations[recommendationType](),
    [allRecommendations, recommendationType]
  );

  return (
    <Accordion expanded={isExpanded} onChange={onChange} disableExpandedSpacing>
      <RecommendationAccordionTitle
        dataTestId={dataTestId}
        messages={[
          <FormattedMessage key={1} id={title} />,
          <KeyValueLabel key={2} keyMessageId="count" value={count} />,
          <FormattedMessage key={3} id={ARCHIVATION_REASON_MESSAGE_ID[reason]} />,
          <KeyValueLabel key={4} keyMessageId="archivedAt" value={`${formatUTC(archivedAt, EN_FULL_FORMAT)} UTC`} />
        ]}
      />
      <Stack spacing={SPACING_1}>
        <div>
          <RecommendationDescription messageId={ARCHIVATION_REASON_DESCRIPTION_MESSAGE_ID[reason]} isLoading={isLoading} />
        </div>
        {count > limit && (
          <div>
            <RecommendationLimitWarning limit={limit} />
          </div>
        )}
        <div>
          <Table
            columns={columns}
            isLoading={isLoading}
            data={items}
            localization={{
              emptyMessageId: "noRecommendations"
            }}
            dataTestIds={{ container: "archived_recommendation_accordion_table" }}
          />
        </div>
      </Stack>
    </Accordion>
  );
};

export default ArchivedRecommendationAccordion;
