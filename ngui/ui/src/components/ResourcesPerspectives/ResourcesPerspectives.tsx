import { useMemo } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import PriorityHighOutlinedIcon from "@mui/icons-material/PriorityHighOutlined";
import { Link, Stack } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import IconLabel from "components/IconLabel";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import DeletePerspectiveSideModal from "components/SideModalManager/SideModals/DeletePerspectiveSideModal";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { useIsAllowed } from "hooks/useAllowedActions";
import { breakdowns } from "hooks/useBreakdownBy";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationPerspectives } from "hooks/useOrganizationPerspectives";
import { getResourcesExpensesUrl } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { SPACING_2 } from "utils/layouts";

const ResourcesPerspectives = () => {
  const isAllowedToDeletePerspectives = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const intl = useIntl();

  const { validPerspectives, invalidPerspectives } = useOrganizationPerspectives();

  const openSideModal = useOpenSideModal();

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_perspective_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        defaultSort: "asc",
        cell: ({ row: { original } }) =>
          original.isInvalid ? (
            <IconLabel
              icon={
                <Tooltip
                  title={
                    <>
                      <FormattedMessage id="perspectiveIsCorrupted" />
                      {isAllowedToDeletePerspectives && (
                        <>
                          <br />
                          <FormattedMessage id="considerDeletingThePerspective" />
                        </>
                      )}
                    </>
                  }
                >
                  <PriorityHighOutlinedIcon fontSize="inherit" color="error" />
                </Tooltip>
              }
              label={original.name}
            />
          ) : (
            <Link
              to={getResourcesExpensesUrl({
                perspective: original.name
              })}
              component={RouterLink}
            >
              {original.name}
            </Link>
          )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_categorize_by">
            <FormattedMessage id="breakdownBy" />
          </TextWithDataTestId>
        ),
        accessorKey: "breakdownBy"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_categorize_by">
            <FormattedMessage id="categorizeBy" />
          </TextWithDataTestId>
        ),
        accessorKey: "categorizeBy"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_group_by">
            <FormattedMessage id="groupBy" />
          </TextWithDataTestId>
        ),
        accessorKey: "groupByString",
        cell: ({ row: { original } }) => {
          const { groupBy } = original;

          if (!groupBy.groupType) {
            return <FormattedMessage id="none" />;
          }
          if (groupBy.groupType === "tag") {
            return <KeyValueLabel keyMessageId={groupBy.groupType} value={groupBy.groupBy} />;
          }
          return <FormattedMessage id={groupBy.groupType} />;
        }
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_filters">
            <FormattedMessage id="filters" />
          </TextWithDataTestId>
        ),
        accessorKey: "filtersString",
        cell: ({ row: { original } }) => {
          const { filters } = original;
          return isEmptyArray(filters)
            ? "-"
            : filters.map(({ name: filterName, displayedName, displayedValue }) => (
                <KeyValueLabel key={filterName} keyText={displayedName} value={displayedValue} />
              ));
        }
      },
      ...(isAllowedToDeletePerspectives
        ? [
            {
              header: (
                <TextWithDataTestId dataTestId="lbl_actions">
                  <FormattedMessage id="actions" />
                </TextWithDataTestId>
              ),
              id: "actions",
              enableSorting: false,
              cell: ({ row: { original, index } }) => (
                <TableCellActions
                  items={[
                    {
                      key: "deletePerspective",
                      messageId: "deletePerspective",
                      icon: <DeleteOutlinedIcon />,
                      color: "error",
                      requiredActions: ["EDIT_PARTNER"],
                      dataTestId: `btn_delete_perspective_${index}`,
                      action: () => {
                        openSideModal(DeletePerspectiveSideModal, { perspectiveName: original.name });
                      }
                    }
                  ]}
                />
              )
            }
          ]
        : [])
    ],
    [isAllowedToDeletePerspectives, openSideModal]
  );

  const data = useMemo(() => {
    const validPerspectivesToTableData = () => {
      const getGroupByString = (groupBy) => {
        if (!groupBy.groupType) {
          return intl.formatMessage({ id: "none" });
        }
        if (groupBy.groupType === "tag") {
          const groupType = intl.formatMessage({ id: groupBy.groupType });
          return `${groupType}: ${groupBy.groupBy}`;
        }
        return intl.formatMessage({ id: groupBy.groupType });
      };

      return Object.entries(validPerspectives).map(
        ([
          perspectiveName,
          {
            breakdownBy,
            breakdownData: { groupBy, breakdownBy: categorizeBy },
            filters: { filterValues, appliedFilters }
          }
        ]) => {
          const filters = new Filters({
            filters: RESOURCE_FILTERS,
            filterValues,
            appliedFilters
          });

          const appliedFilterValues = filters.getAppliedValues();

          return {
            name: perspectiveName,
            filters: filters.getAppliedValues(),
            filtersString: appliedFilterValues
              .map(({ displayedNameString, displayedValueString }) => `${displayedNameString}: ${displayedValueString}`)
              .join(" "),
            breakdownBy: intl.formatMessage({ id: breakdownBy }),
            categorizeBy: breakdowns.find((breakdown) => breakdown.value === categorizeBy)?.name ?? undefined,
            groupBy,
            groupByString: groupBy ? getGroupByString(groupBy) : undefined
          };
        }
      );
    };

    const invalidPerspectivesToTableData = () =>
      Object.keys(invalidPerspectives).map((perspectiveName) => ({
        name: perspectiveName,
        isInvalid: true
      }));

    return [...validPerspectivesToTableData(), ...invalidPerspectivesToTableData()];
  }, [validPerspectives, intl, invalidPerspectives]);

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <Table
          columns={columns}
          data={data}
          localization={{
            emptyMessageId: "noPerspectives"
          }}
          withSearch
          pageSize={50}
        />
      </div>
      <div>
        <InlineSeverityAlert messageId="perspectivesDescription" />
      </div>
    </Stack>
  );
};

export default ResourcesPerspectives;
