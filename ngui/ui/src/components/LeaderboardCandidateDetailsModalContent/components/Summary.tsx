import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CollapsableTableCell from "components/CollapsableTableCell";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import ExpandableList from "components/ExpandableList";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import LeaderboardDatasetsCoverageRules from "components/LeaderboardDatasetsCoverageRules";
import SubTitle from "components/SubTitle";
import SummaryList from "components/SummaryList";
import { isEmpty as isEmptyObject } from "utils/objects";

const Coverage = ({ coverage }) => (
  <Box>
    <SubTitle>
      <FormattedMessage id="coverage" />
    </SubTitle>
    <LeaderboardDatasetsCoverageRules datasets={coverage.datasets} coverageRules={coverage.coverageRules} />
  </Box>
);

const Summary = ({ tags, metrics, hyperparameters, coverage }) => (
  <Box display="flex" flexWrap="wrap" rowGap={1} columnGap={16}>
    <Box>
      <SummaryList
        titleMessage={<FormattedMessage id="aggregatedMetrics" />}
        items={
          <ExpandableList
            items={Object.entries(metrics).sort(([nameA], [nameB]) => nameA.localeCompare(nameB))}
            render={([name, value]) => (
              <KeyValueLabel
                key={name}
                keyText={name}
                value={value !== null ? <DynamicFractionDigitsValue value={value} /> : undefined}
              />
            )}
            maxRows={5}
          />
        }
      />
    </Box>
    <Coverage coverage={coverage} />
    <Box>
      <SummaryList titleMessage={<FormattedMessage id="tags" />} items={<CollapsableTableCell maxRows={5} tags={tags} />} />
    </Box>
    {!isEmptyObject(hyperparameters) && (
      <Box>
        <SummaryList
          titleMessage={<FormattedMessage id="hyperparameters" />}
          items={<CollapsableTableCell maxRows={5} tags={hyperparameters} />}
        />
      </Box>
    )}
  </Box>
);
export default Summary;
