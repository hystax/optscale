import { Autocomplete, Box, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import Input from "components/Input";
import SlicedText from "components/SlicedText";
import { useIsAllowed } from "hooks/useAllowedActions";
import { isEmpty as isEmptyArray } from "utils/arrays";
import CopyLeaderboardIconButton from "./CopyLeaderboardIconButton";
import CreateLeaderboardIconButton from "./CreateLeaderboardIconButton";
import DeleteLeaderboardButton from "./DeleteLeaderboardButton";
import EditLeaderboardIconButton from "./EditLeaderboardIconButton";
import LeaderboardDetails from "./LeaderboardDetails";

const NoLeaderboards = ({ leaderboardTemplate, task, onCreateLeaderboard }) => {
  const isCreateLeaderboardAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return (
    <Box display="flex" alignItems="center" gap={1}>
      <Typography>
        <FormattedMessage id="noLeaderboards" />
      </Typography>
      {isCreateLeaderboardAllowed && (
        <CreateLeaderboardIconButton leaderboardTemplate={leaderboardTemplate} task={task} onSuccess={onCreateLeaderboard} />
      )}
    </Box>
  );
};

const LeaderboardsListSection = ({
  task,
  leaderboardTemplate,
  leaderboards,
  leaderboard,
  selectedLeaderboardId,
  onSelectedLeaderboardIdChange,
  onCreateLeaderboard,
  onUpdateLeaderboard,
  onDeleteLeaderboard
}) => {
  const isManageLeaderboardAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return (
    <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
      <Autocomplete
        options={leaderboards}
        getOptionKey={(option) => option.id}
        getOptionLabel={(option) => option?.name ?? ""}
        value={leaderboards.find(({ id }) => id === selectedLeaderboardId) ?? ""}
        isOptionEqualToValue={(option, value) => option.id === value.id}
        onChange={(event, newValue) => {
          if (newValue) {
            onSelectedLeaderboardIdChange(newValue.id);
          }
        }}
        blurOnSelect
        sx={{
          maxWidth: "450px",
          flexBasis: "280px",
          flexGrow: 1
        }}
        renderOption={(props, option) => {
          const { name, primary_metric: { name: primaryMetricName, value: primaryMetricValue } = {} } = option;

          return (
            <li {...props}>
              <Box display="flex" flexDirection="column">
                <Typography variant="body2">
                  <SlicedText text={name} limit={25} />
                </Typography>
                <Typography variant="caption">
                  <SlicedText text={primaryMetricName} limit={15} />
                  &#58;&nbsp;
                  <strong>
                    {primaryMetricValue === null ? "-" : <DynamicFractionDigitsValue value={primaryMetricValue} />}
                  </strong>
                </Typography>
              </Box>
            </li>
          );
        }}
        renderInput={(autoCompleteParams) => <Input label={<FormattedMessage id="leaderboard" />} {...autoCompleteParams} />}
      />
      {isManageLeaderboardAllowed && (
        <Box>
          <CreateLeaderboardIconButton leaderboardTemplate={leaderboardTemplate} task={task} onSuccess={onCreateLeaderboard} />
          <EditLeaderboardIconButton task={task} leaderboard={leaderboard} onSuccess={onUpdateLeaderboard} />
          <CopyLeaderboardIconButton
            task={task}
            leaderboardTemplate={leaderboardTemplate}
            leaderboard={leaderboard}
            onSuccess={onCreateLeaderboard}
          />
          <DeleteLeaderboardButton leaderboard={leaderboard} onSuccess={onDeleteLeaderboard} />
        </Box>
      )}
    </Box>
  );
};

const Leaderboards = ({
  task,
  leaderboardTemplate,
  leaderboards = [],
  leaderboard,
  leaderboardCandidates,
  selectedLeaderboardId,
  onSelectedLeaderboardIdChange,
  onCreateLeaderboard,
  onUpdateLeaderboard,
  onDeleteLeaderboard,
  isLoadingProps = {}
}) => (
  <Box>
    {isEmptyArray(leaderboards) ? (
      <NoLeaderboards leaderboardTemplate={leaderboardTemplate} task={task} onCreateLeaderboard={onCreateLeaderboard} />
    ) : (
      <Stack spacing={1}>
        <div>
          <LeaderboardsListSection
            task={task}
            leaderboardTemplate={leaderboardTemplate}
            leaderboards={leaderboards}
            leaderboard={leaderboard}
            selectedLeaderboardId={selectedLeaderboardId}
            onSelectedLeaderboardIdChange={onSelectedLeaderboardIdChange}
            onCreateLeaderboard={onCreateLeaderboard}
            onUpdateLeaderboard={onUpdateLeaderboard}
            onDeleteLeaderboard={onDeleteLeaderboard}
          />
        </div>
        <div>
          <LeaderboardDetails
            leaderboard={leaderboard}
            leaderboardCandidates={leaderboardCandidates}
            isLoadingProps={{
              isGetLeaderboardLoading: isLoadingProps.isGetLeaderboardLoading,
              isGetLeaderboardCandidatesLoading: isLoadingProps.isGetLeaderboardCandidatesLoading
            }}
          />
        </div>
      </Stack>
    )}
  </Box>
);

export default Leaderboards;
