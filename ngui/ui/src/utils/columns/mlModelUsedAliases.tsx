import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import ExpandableList from "components/ExpandableList";
import LabelChip from "components/LabelChip";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { CELL_EMPTY_VALUE } from "utils/tables";

const ALIASED_VERSIONS_SHOW_MORE_LIMIT = 3;

const getAliasedVersionString = (version: string, alias: string) => `${alias}: ${version}` as const;

const mlModelUsedAliases = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_used_aliases">
      <FormattedMessage id="usedAliases" />
    </TextWithDataTestId>
  ),
  id: "usedAliases",
  enableSorting: false,
  style: {
    maxWidth: "350px"
  },
  accessorFn: ({ aliased_versions: aliasedVersions = [] }) =>
    aliasedVersions.map(({ version, alias }) => getAliasedVersionString(version, alias)).join(" "),
  cell: ({ row: { original } }) => {
    const { aliased_versions: aliasedVersions } = original;

    if (isEmptyArray(aliasedVersions)) {
      return CELL_EMPTY_VALUE;
    }

    return (
      <Box display="flex" flexWrap="wrap" gap={1}>
        <ExpandableList
          items={aliasedVersions}
          render={(item) => {
            const versionAliasString = getAliasedVersionString(item.version, item.alias);

            return (
              <LabelChip key={versionAliasString} label={versionAliasString} colorizeBy={item.alias} labelSymbolsLimit={40} />
            );
          }}
          maxRows={ALIASED_VERSIONS_SHOW_MORE_LIMIT}
        />
      </Box>
    );
  }
});

export default mlModelUsedAliases;
