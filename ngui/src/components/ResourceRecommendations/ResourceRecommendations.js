import React, { useMemo } from "react";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import WidgetTitle from "components/WidgetTitle";
import { useIsAllowed } from "hooks/useAllowedActions";
import { isEmpty as isEmptyArray } from "utils/arrays";
import {
  BE_TO_FE_MAP_RECOMMENDATION_TYPES,
  RESOURCE_VISIBILITY_ACTIONS,
  FORMATTED_MONEY_TYPES,
  SCOPE_TYPES,
  ACTIONABLE_RECOMMENDATIONS
} from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const ResourceRecommendationTitle = ({ messageId }) => (
  <WidgetTitle dataTestId={`lbl_${messageId}`}>
    <FormattedMessage id={messageId} />
  </WidgetTitle>
);

const ResourceRecommendationLayout = ({ title, table }) => (
  <>
    <Grid item>{title}</Grid>
    <Grid item>{table}</Grid>
  </>
);

const DismissedResourceRecommendations = ({
  patchResource,
  dismissedRecommendations = [],
  shouldRenderTableActions,
  isLoading
}) => {
  const data = useMemo(() => dismissedRecommendations, [dismissedRecommendations]);
  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_table_dismissed_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        defaultSort: "asc",
        cell: ({ cell }) => <FormattedMessage id={BE_TO_FE_MAP_RECOMMENDATION_TYPES[cell.getValue()]} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_table_dismissed_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        enableSorting: false,
        id: "actions",
        cell: ({ row: { original, index } }) => (
          <IconButton
            dataTestId={`btn_dismiss_${index}`}
            isLoading={isLoading}
            icon={<VisibilityOutlinedIcon />}
            onClick={() => patchResource(original.name, RESOURCE_VISIBILITY_ACTIONS.ACTIVATE)}
            disabled={!shouldRenderTableActions}
            tooltip={{
              show: true,
              value: (
                <FormattedMessage id={shouldRenderTableActions ? "activateRecommendation" : "youDoNotHaveEnoughPermissions"} />
              )
            }}
          />
        )
      }
    ],
    [isLoading, patchResource, shouldRenderTableActions]
  );
  return (
    <ResourceRecommendationLayout
      title={<ResourceRecommendationTitle messageId="dismissed" />}
      table={
        <Table
          dataTestIds={{
            container: "table_dismissed"
          }}
          data={data}
          columns={columns}
          localization={{
            emptyMessageId: "noDismissedRecommendations"
          }}
        />
      }
    />
  );
};

const ActiveResourceRecommendations = ({ patchResource, activeRecommendations = [], shouldRenderTableActions, isLoading }) => {
  const data = useMemo(() => activeRecommendations, [activeRecommendations]);
  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_table_active_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        cell: ({ row: { original } }) => (
          <FormattedMessage
            values={{
              size: original.recommended_flavor,
              regionName: original.recommended_region,
              recommendedSize: original.recommended_flavor,
              groupName: original.security_group_name
            }}
            id={`${BE_TO_FE_MAP_RECOMMENDATION_TYPES[original.name]}ResourceRecommendation`}
          />
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_table_active_savings">
            <FormattedMessage id="possibleMonthlySavings" />
          </TextWithDataTestId>
        ),
        accessorKey: "saving",
        defaultSort: "desc",
        cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_table_active_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        enableSorting: false,
        id: "actions",
        cell: ({ row: { original, index } }) =>
          ACTIONABLE_RECOMMENDATIONS.includes(original.name) && (
            <IconButton
              dataTestId={`btn_activate_${index}`}
              isLoading={isLoading}
              icon={<VisibilityOffOutlinedIcon />}
              onClick={() => patchResource(original.name, RESOURCE_VISIBILITY_ACTIONS.DISMISS)}
              disabled={!shouldRenderTableActions}
              tooltip={{
                show: true,
                value: (
                  <FormattedMessage id={shouldRenderTableActions ? "dismissRecommendation" : "youDoNotHaveEnoughPermissions"} />
                )
              }}
            />
          )
      }
    ],
    [isLoading, patchResource, shouldRenderTableActions]
  );
  return (
    <ResourceRecommendationLayout
      title={<ResourceRecommendationTitle messageId="active" />}
      table={
        <Table
          dataTestIds={{
            container: "table_active"
          }}
          data={data}
          columns={columns}
          localization={{
            emptyMessageId: "noRecommendations"
          }}
        />
      }
    />
  );
};

const ResourceRecommendations = ({
  recommendations,
  dismissedRecommendations,
  patchResource,
  resourceId,
  isLoading = false
}) => {
  const shouldRenderTableActions = useIsAllowed({
    entityType: SCOPE_TYPES.RESOURCE,
    entityId: resourceId,
    requiredActions: ["MANAGE_RESOURCES", "MANAGE_OWN_RESOURCES"]
  });

  return (
    <Grid container direction="column" spacing={SPACING_2}>
      {!isEmptyArray(recommendations) && (
        <ActiveResourceRecommendations
          activeRecommendations={recommendations}
          patchResource={patchResource}
          shouldRenderTableActions={shouldRenderTableActions}
          isLoading={isLoading}
        />
      )}
      {!isEmptyArray(dismissedRecommendations) && (
        <DismissedResourceRecommendations
          dismissedRecommendations={dismissedRecommendations}
          patchResource={patchResource}
          shouldRenderTableActions={shouldRenderTableActions}
          isLoading={isLoading}
        />
      )}
    </Grid>
  );
};

ResourceRecommendationTitle.propTypes = {
  messageId: PropTypes.string.isRequired
};

ResourceRecommendationLayout.propTypes = {
  table: PropTypes.node.isRequired,
  title: PropTypes.node.isRequired
};

DismissedResourceRecommendations.propTypes = {
  shouldRenderTableActions: PropTypes.bool,
  patchResource: PropTypes.func,
  isLoading: PropTypes.bool,
  dismissedRecommendations: PropTypes.array
};

ActiveResourceRecommendations.propTypes = {
  shouldRenderTableActions: PropTypes.bool,
  patchResource: PropTypes.func,
  isLoading: PropTypes.bool,
  activeRecommendations: PropTypes.array
};

ResourceRecommendations.propTypes = {
  resourceId: PropTypes.string.isRequired,
  recommendations: PropTypes.array,
  dismissedRecommendations: PropTypes.array,
  isLoading: PropTypes.bool,
  patchResource: PropTypes.func
};

export default ResourceRecommendations;
