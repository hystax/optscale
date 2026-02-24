import { useMemo } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import PriorityHighOutlinedIcon from "@mui/icons-material/PriorityHighOutlined";
import { Link } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { FILTER_TYPE } from "components/FilterComponents/constants";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import PageContentDescription from "components/PageContentDescription";
import { FILTER_CONFIGS } from "components/Resources/filterConfigs";
import DeletePerspectiveSideModal from "components/SideModalManager/SideModals/DeletePerspectiveSideModal";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { useOrganizationPerspectives } from "hooks/coreData/useOrganizationPerspectives";
import { useIsAllowed } from "hooks/useAllowedActions";
import { breakdowns } from "hooks/useBreakdownBy";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { getResourcesExpensesUrl } from "urls";
import { isEmptyArray } from "utils/arrays";
import { CELL_EMPTY_VALUE } from "utils/tables";

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
                perspective: original.name,
              })}
              component={RouterLink}
            >
              {original.name}
            </Link>
          ),
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_categorize_by">
            <FormattedMessage id="breakdownBy" />
          </TextWithDataTestId>
        ),
        accessorKey: "breakdownBy",
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_categorize_by">
            <FormattedMessage id="categorizeBy" />
          </TextWithDataTestId>
        ),
        accessorKey: "categorizeBy",
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
        },
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
            ? CELL_EMPTY_VALUE
            : filters.map(({ displayedName, displayedValue, displayedNameString, displayedValueString }) => (
                <KeyValueLabel
                  key={`${displayedNameString}-${displayedValueString}`}
                  keyText={displayedName}
                  value={displayedValue}
                />
              ));
        },
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
                      },
                    },
                  ]}
                />
              ),
            },
          ]
        : []),
    ],
    [isAllowedToDeletePerspectives, openSideModal]
  );

  const tableData = useMemo(() => {
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
            filters: { filterValues, appliedFilters },
          },
        ]) => {
          const perspectiveFilters = Object.values(FILTER_CONFIGS).flatMap((filterConfig) => {
            if (filterConfig.type === FILTER_TYPE.SELECTION) {
              const appliedFilterValues = appliedFilters[filterConfig.id];

              if (isEmptyArray(appliedFilterValues)) {
                return [];
              }

              return appliedFilterValues.map((appliedFilterValue) => ({
                displayedName: filterConfig.label,
                displayedValue: filterConfig.renderPerspectiveItem(appliedFilterValue, filterValues[filterConfig.apiName]),
                displayedNameString: filterConfig.labelString,
                displayedValueString: filterConfig.renderPerspectiveItem(
                  appliedFilterValue,
                  filterValues[filterConfig.apiName],
                  { stringify: true }
                ),
              }));
            }
            if (filterConfig.type === FILTER_TYPE.RANGE) {
              const from = appliedFilters[filterConfig.fromName];
              const to = appliedFilters[filterConfig.toName];

              if (!from && !to) {
                return [];
              }

              return [
                {
                  displayedName: filterConfig.label,
                  displayedValue: filterConfig.renderPerspectiveItem({
                    from,
                    to,
                  }),
                  displayedNameString: filterConfig.labelString,
                  displayedValueString: filterConfig.renderPerspectiveItem({
                    from,
                    to,
                  }),
                },
              ];
            }
            return [];
          });

          const getCategorizeBy = () => {
            const breakdownDefinition = breakdowns.find((breakdown) => breakdown.value === categorizeBy);

            if (breakdownDefinition) {
              return breakdownDefinition.name;
            }

            return intl.formatMessage({ id: categorizeBy });
          };

          return {
            name: perspectiveName,
            filters: perspectiveFilters,
            filtersString: perspectiveFilters
              .map(({ displayedNameString, displayedValueString }) => `${displayedNameString}: ${displayedValueString}`)
              .join(" "),
            breakdownBy: intl.formatMessage({ id: breakdownBy }),
            categorizeBy: categorizeBy ? getCategorizeBy() : undefined,
            groupBy,
            groupByString: groupBy ? getGroupByString(groupBy) : undefined,
          };
        }
      );
    };

    const invalidPerspectivesToTableData = () =>
      Object.keys(invalidPerspectives).map((perspectiveName) => ({
        name: perspectiveName,
        isInvalid: true,
      }));

    return [...validPerspectivesToTableData(), ...invalidPerspectivesToTableData()];
  }, [validPerspectives, intl, invalidPerspectives]);

  return (
    <>
      <Table
        columns={columns}
        data={tableData}
        localization={{
          emptyMessageId: "noPerspectives",
        }}
        withSearch
        pageSize={50}
      />
      <PageContentDescription
        position="bottom"
        alertProps={{
          messageId: "perspectivesDescription",
        }}
      />
    </>
  );
};

export default ResourcesPerspectives;
