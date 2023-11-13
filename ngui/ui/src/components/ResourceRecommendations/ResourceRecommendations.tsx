import { useMemo } from "react";
import VisibilityOffOutlinedIcon from "@mui/icons-material/VisibilityOffOutlined";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import Grid from "@mui/material/Grid";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import WidgetTitle from "components/WidgetTitle";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { RESOURCE_VISIBILITY_ACTIONS, FORMATTED_MONEY_TYPES, SCOPE_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const descriptionColumn = (state) => ({
  header: (
    <TextWithDataTestId dataTestId={`lbl_table_${state}_name`}>
      <FormattedMessage id="description" />
    </TextWithDataTestId>
  ),
  accessorKey: "name",
  cell: ({ row: { original } }) => (
    <FormattedMessage values={original.descriptionMessageValues} id={original.descriptionMessageId} />
  )
});

const actionsColumn = ({ active = true, isLoading, patchResource, shouldRenderTableActions }) => ({
  header: (
    <TextWithDataTestId dataTestId={`lbl_table_${active ? "active" : "dismissed"}_actions`}>
      <FormattedMessage id="actions" />
    </TextWithDataTestId>
  ),
  enableSorting: false,
  accessorKey: "dismissable",
  cell: ({ cell, row: { original, index } }) =>
    cell.getValue() && (
      <IconButton
        dataTestId={`btn_${active ? "activate" : "dismiss"}_${index}`}
        isLoading={isLoading}
        icon={active ? <VisibilityOffOutlinedIcon /> : <VisibilityOutlinedIcon />}
        onClick={() =>
          patchResource(original.name, active ? RESOURCE_VISIBILITY_ACTIONS.DISMISS : RESOURCE_VISIBILITY_ACTIONS.ACTIVATE)
        }
        disabled={!shouldRenderTableActions}
        tooltip={{
          show: true,
          value: shouldRenderTableActions ? (
            <FormattedMessage id={active ? "dismissRecommendation" : "activateRecommendation"} />
          ) : (
            <FormattedMessage id="youDoNotHaveEnoughPermissions" />
          )
        }}
      />
    )
});

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
      descriptionColumn("dismissed"),
      actionsColumn({ active: false, isLoading, patchResource, shouldRenderTableActions })
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
      descriptionColumn("active"),
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
      actionsColumn({ active: true, isLoading, patchResource, shouldRenderTableActions })
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

const patchRecommendationWithDescriptions = (backendData, RecommendationClass) => ({
  ...backendData,
  descriptionMessageId: RecommendationClass.resourceDescriptionMessageId,
  descriptionMessageValues: RecommendationClass.getResourceDescriptionMessageValues(backendData),
  dismissable: new RecommendationClass("active", {}).dismissable
});

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

  const allRecommendations = useAllRecommendations();

  const recommendationsWithInfo = recommendations.map((recommendationDatum) =>
    patchRecommendationWithDescriptions(recommendationDatum, allRecommendations[recommendationDatum.name])
  );
  const dismissedRecommendationsWithInfo = dismissedRecommendations.map((recommendationDatum) =>
    patchRecommendationWithDescriptions(recommendationDatum, allRecommendations[recommendationDatum.name])
  );

  return (
    <Grid container direction="column" spacing={SPACING_2}>
      {!isEmptyArray(recommendationsWithInfo) && (
        <ActiveResourceRecommendations
          activeRecommendations={recommendationsWithInfo}
          patchResource={patchResource}
          shouldRenderTableActions={shouldRenderTableActions}
          isLoading={isLoading}
        />
      )}
      {!isEmptyArray(dismissedRecommendationsWithInfo) && (
        <DismissedResourceRecommendations
          dismissedRecommendations={dismissedRecommendationsWithInfo}
          patchResource={patchResource}
          shouldRenderTableActions={shouldRenderTableActions}
          isLoading={isLoading}
        />
      )}
    </Grid>
  );
};

export default ResourceRecommendations;
