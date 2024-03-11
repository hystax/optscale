import CheckCircleOutlinedIcon from "@mui/icons-material/CheckCircleOutlined";
import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CollapsableTableCell from "components/CollapsableTableCell";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import ExpandableList from "components/ExpandableList";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import ProgressBar from "components/ProgressBar";
import SubTitle from "components/SubTitle";
import SummaryList from "components/SummaryList";
import { ERROR } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";

const Summary = ({ tags, metrics, hyperparameters, coverage }) => {
  const qualificationProgress = (coverage.covered / coverage.all) * 100;
  const qualificationText = `${coverage.covered}/${coverage.all}`;

  return (
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
      <Box>
        <SubTitle>
          <FormattedMessage id="datasetsCoverage" />
        </SubTitle>
        {qualificationProgress === 100 ? (
          <IconLabel
            icon={<CheckCircleOutlinedIcon fontSize="inherit" color="success" />}
            label={<Typography fontWeight="bold">{qualificationText}</Typography>}
          />
        ) : (
          <ProgressBar
            height="1.5rem"
            wrapperSx={{ minWidth: "150px", marginTop: SPACING_1 }}
            color={ERROR}
            value={qualificationProgress}
          >
            <Typography>{qualificationText}</Typography>
          </ProgressBar>
        )}
      </Box>
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
};

export default Summary;
