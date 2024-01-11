import { Fragment, useMemo } from "react";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import ZoomInIcon from "@mui/icons-material/ZoomIn";
import { Divider, Stack } from "@mui/material";
import { Box } from "@mui/system";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import IconLabel from "components/IconLabel";
import SubTitle from "components/SubTitle";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import { formatSecondsToHHMMSS, millisecondsToSeconds } from "utils/datetime";

const ZOOM_MILESTONE_SECONDS_RANGE = 5;

const MilestonesTable = ({ milestones, onMilestoneZoom }) => {
  const tableData = useMemo(
    () =>
      milestones.map(([second, milestoneNames]) => ({
        second,
        milestoneNames
      })),
    [milestones]
  );

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_milestones">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "milestoneNames",
        enableSorting: false,
        cell: ({ cell, row: { original }, index }) => (
          <Box display="flex" alignItems="center">
            <div>
              {cell.getValue().map((name) => (
                <div key={name}>{name}</div>
              ))}
            </div>
            <IconButton
              icon={<ZoomInIcon />}
              onClick={() => onMilestoneZoom(original.second)}
              dataTestId={`btn_select_milestone_${index}`}
              tooltip={{
                show: true,
                messageId: "zoom"
              }}
            />
          </Box>
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_time">
            <FormattedMessage id="time" />
          </TextWithDataTestId>
        ),
        accessorKey: "second",
        cell: ({ cell }) => formatSecondsToHHMMSS(cell.getValue()),
        defaultSort: "asc"
      }
    ],
    [onMilestoneZoom]
  );

  return (
    <Table
      data={tableData}
      columns={columns}
      localization={{
        emptyMessageId: "noMilestones"
      }}
    />
  );
};

const StagesTable = ({ stages, onStageZoom, onStageHighlight, isStageHighlighted }) => {
  const tableData = useMemo(() => stages, [stages]);

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        cell: ({ cell, row: { original }, index }) => {
          const value = cell.getValue();
          const isHighlighted = isStageHighlighted(original);
          return (
            <IconLabel
              endIcon={
                original.end ? (
                  <>
                    <IconButton
                      icon={<ZoomInIcon />}
                      onClick={() => onStageZoom(original.start, original.end)}
                      dataTestId={`btn_zoom_stage_${index}`}
                      tooltip={{
                        show: true,
                        messageId: "zoom"
                      }}
                    />
                    <IconButton
                      icon={<VisibilityOutlinedIcon color={isHighlighted ? "secondary" : "info"} />}
                      onClick={() =>
                        onStageHighlight(
                          isHighlighted
                            ? null
                            : {
                                name: value,
                                start: original.start,
                                end: original.end
                              }
                        )
                      }
                      dataTestId={`btn_highlight_stage_${index}`}
                      tooltip={{
                        show: true,
                        messageId: isHighlighted ? "removeHighlight" : "highlight"
                      }}
                    />
                  </>
                ) : null
              }
              label={value}
            />
          );
        }
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_time">
            <FormattedMessage id="time" />
          </TextWithDataTestId>
        ),
        accessorKey: "start",
        cell: ({
          row: {
            original: { start, end, startTimestamp }
          }
        }) => {
          const formattedStart = formatSecondsToHHMMSS(start);
          const formattedEnd = end ? formatSecondsToHHMMSS(end) : null;

          return end ? (
            <>
              <div>
                <FormattedMessage
                  id="value - value"
                  values={{
                    value1: formattedStart,
                    value2: formattedEnd
                  }}
                />
              </div>
              <div>{formatSecondsToHHMMSS(end - start)}</div>
            </>
          ) : (
            <>
              <div>{formattedStart}</div>
              <div>
                <FormattedMessage
                  id="runningForX"
                  values={{
                    x: formatSecondsToHHMMSS(millisecondsToSeconds(+new Date()) - startTimestamp)
                  }}
                />
              </div>
            </>
          );
        },
        defaultSort: "asc"
      }
    ],
    [isStageHighlighted, onStageHighlight, onStageZoom]
  );

  return (
    <Table
      data={tableData}
      columns={columns}
      localization={{
        emptyMessageId: "noStages"
      }}
    />
  );
};

const StagesAndMilestones = ({
  milestonesGroupedByTimeTuples,
  resetBrushTo,
  stages,
  highlightedStage,
  setHighlightedStage,
  secondsTimeRange
}) => {
  const isUpSm = useIsUpMediaQuery("sm");

  return (
    <Stack spacing={2} divider={isUpSm ? <Divider orientation="vertical" flexItem /> : null}>
      <div>
        <SubTitle>
          <FormattedMessage id="stages" />
        </SubTitle>
        <StagesTable
          stages={stages}
          onStageZoom={(start, end) => resetBrushTo(start, end)}
          isStageHighlighted={(stage) => {
            if (highlightedStage === null) {
              return false;
            }
            return (
              stage.name === highlightedStage.name &&
              stage.start === highlightedStage.start &&
              stage.end === highlightedStage.end
            );
          }}
          onStageHighlight={(stage) => setHighlightedStage(stage)}
        />
      </div>
      <div>
        <SubTitle>
          <FormattedMessage id="milestones" />
        </SubTitle>
        <MilestonesTable
          milestones={milestonesGroupedByTimeTuples}
          onMilestoneZoom={(second) => {
            const min = Math.max(second - ZOOM_MILESTONE_SECONDS_RANGE, secondsTimeRange[0]);
            const max = Math.min(second + ZOOM_MILESTONE_SECONDS_RANGE, secondsTimeRange[1]);

            return resetBrushTo(min, max);
          }}
        />
      </div>
    </Stack>
  );
};

export default StagesAndMilestones;
