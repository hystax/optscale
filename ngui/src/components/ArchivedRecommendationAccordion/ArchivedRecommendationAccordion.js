import React, { useEffect, useMemo } from "react";
import { Stack } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { getArchivedOptimizationDetails } from "api";
import { GET_ARCHIVED_OPTIMIZATION_DETAILS } from "api/restapi/actionTypes";
import Accordion from "components/Accordion";
import KeyValueLabel from "components/KeyValueLabel";
import RecommendationAccordionTitle from "components/RecommendationAccordionTitle";
import RecommendationDescription from "components/RecommendationDescription";
import RecommendationLimitWarning from "components/RecommendationLimitWarning";
import { getRecommendationInstanceByType } from "components/RelevantRecommendations";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import {
  ARCHIVATION_REASON_DESCRIPTION_MESSAGE_ID,
  ARCHIVATION_REASON_MESSAGE_ID,
  BE_TO_FE_MAP_RECOMMENDATION_TYPES,
  RECOMMENDATIONS_LIMIT_FILTER
} from "utils/constants";
import { EN_FULL_FORMAT, formatUTC } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";

const ArchivedRecommendationAccordion = ({ recommendationType, count, reason, archivedAt, onChange, isExpanded = false }) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { items = [] }
  } = useApiData(GET_ARCHIVED_OPTIMIZATION_DETAILS, {});

  const { isLoading, shouldInvoke } = useApiState(GET_ARCHIVED_OPTIMIZATION_DETAILS, {
    organizationId,
    type: recommendationType,
    archivedAt,
    reason
  });

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

  /* 
    TODO: create getRecommendationInstanceByModuleName util and use it here:
    For examples: 
      const recommendationInstance = getRecommendationInstanceByModuleName(recommendationType);
  */
  const recommendationInstance = getRecommendationInstanceByType(BE_TO_FE_MAP_RECOMMENDATION_TYPES[recommendationType]);

  const columns = useMemo(() => recommendationInstance.constructor.configureColumns({}), [recommendationInstance]);

  return (
    <Accordion expanded={isExpanded} onChange={onChange} disableExpandedSpacing>
      <RecommendationAccordionTitle
        messages={[
          <FormattedMessage key={1} id={recommendationInstance.messageId} />,
          <KeyValueLabel key={2} messageId="count" value={count} />,
          <FormattedMessage key={3} id={ARCHIVATION_REASON_MESSAGE_ID[reason]} />,
          <KeyValueLabel key={4} messageId="archivedAt" value={`${formatUTC(archivedAt, EN_FULL_FORMAT)} UTC`} />
        ]}
      />
      <Stack spacing={SPACING_1}>
        <RecommendationDescription messageId={ARCHIVATION_REASON_DESCRIPTION_MESSAGE_ID[reason]} isLoading={isLoading} />
        {isLoading ? (
          <TableLoader columnsCounter={columns.length} />
        ) : (
          <>
            {count > items.length && <RecommendationLimitWarning limit={RECOMMENDATIONS_LIMIT_FILTER} />}
            <Table
              columns={columns}
              data={items}
              localization={{
                emptyMessageId: "noRecommendations"
              }}
            />
          </>
        )}
      </Stack>
    </Accordion>
  );
};

ArchivedRecommendationAccordion.propTypes = {
  recommendationType: PropTypes.string.isRequired,
  count: PropTypes.number.isRequired,
  isExpanded: PropTypes.bool.isRequired,
  reason: PropTypes.string.isRequired,
  archivedAt: PropTypes.number.isRequired,
  onChange: PropTypes.func.isRequired
};

export default ArchivedRecommendationAccordion;
