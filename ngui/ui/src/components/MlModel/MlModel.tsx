import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import { Box, Link, Typography } from "@mui/material";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate, useParams } from "react-router-dom";
import { GET_ML_MODEL } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import CollapsableTableCell from "components/CollapsableTableCell";
import ExpandableList from "components/ExpandableList";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel";
import LabelChip from "components/LabelChip";
import Markdown from "components/Markdown";
import MlModelPathLabel from "components/MlModelPathLabel";
import PageContentWrapper from "components/PageContentWrapper";
import {
  EditModelPathModal,
  EditModelVersionAliasModal,
  EditModelVersionTagsModal
} from "components/SideModalManager/SideModals";
import SubTitle from "components/SubTitle";
import SummaryList from "components/SummaryList";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import TypographyLoader from "components/TypographyLoader";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useRefetchApis } from "hooks/useRefetchApis";
import { ModelDetails } from "services/MlModelsService";
import { ML_MODELS, getEditMlModelUrl } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { mlModelPath, mlModelVersion, run, utcTime } from "utils/columns";
import { unixTimestampToDateTime } from "utils/datetime";
import { SPACING_1, SPACING_2 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";
import { PickRename } from "utils/types";

type MlModelProps = {
  model: ModelDetails;
  isLoading: boolean;
};

type DescriptionProps = Pick<ModelDetails, "description"> & {
  isLoading: boolean;
};

type SummaryProps = PickRename<
  ModelDetails,
  {
    name: "name";
    key: "modelKey";
    created_at: "createdAt";
    tags: "tags";
  }
> & {
  isLoading: boolean;
};

type VersionProps = Pick<ModelDetails, "versions"> & {
  isLoading: boolean;
};

const Description = ({ description = "", isLoading = false }: DescriptionProps) => {
  if (isLoading) {
    return <TypographyLoader linesCount={4} />;
  }

  return description ? <Markdown>{description}</Markdown> : null;
};

const Summary = ({ name = "", modelKey = "", createdAt = 0, tags = {}, isLoading = false }: SummaryProps) => (
  <Box display="flex" flexWrap="wrap" rowGap={1} columnGap={16}>
    <Box>
      <SummaryList
        titleMessage={<FormattedMessage id="summary" />}
        items={[
          <KeyValueLabel key="name" keyMessageId="name" value={name} />,
          <KeyValueLabel key="key" keyMessageId="key" value={modelKey} />,
          <KeyValueLabel key="createdAt" keyMessageId="createdAt" value={unixTimestampToDateTime(createdAt)} />
        ]}
        isLoading={isLoading}
      />
    </Box>
    <Box>
      <SummaryList
        titleMessage={<FormattedMessage id="tags" />}
        items={
          isEmptyObject(tags) ? (
            <Typography>
              <FormattedMessage id="noTags" />
            </Typography>
          ) : (
            <ExpandableList
              items={Object.entries(tags).sort(([nameA], [nameB]) => nameA.localeCompare(nameB))}
              render={([tagName, tagValue]) => <KeyValueLabel key={tagName} keyText={tagName} value={tagValue} />}
              maxRows={5}
            />
          )
        }
        isLoading={isLoading}
      />
    </Box>
  </Box>
);

const Version = ({ versions = [], isLoading = false }: VersionProps) => {
  const tableData = useMemo(() => versions, [versions]);
  const { modelId } = useParams() as { modelId: string };
  const openSideModal = useOpenSideModal();

  const isManageVersionAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const aliasToVersionMap = useMemo(
    () => Object.fromEntries(versions.flatMap((version) => version.aliases.map((alias) => [alias, version.version]))),
    [versions]
  );

  const columns = useMemo(
    () => [
      mlModelVersion({
        headerMessageId: "version",
        headerDataTestId: "lbl_version",
        accessorKey: "version"
      }),
      utcTime({
        id: "registeredAt",
        accessorFn: (originalRow) => originalRow.created_at,
        headerMessageId: "registeredAt",
        headerDataTestId: "lbl_registered_at",
        defaultSort: "desc"
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_aliases">
            <FormattedMessage id="aliases" />
          </TextWithDataTestId>
        ),
        id: "aliases",
        accessorFn: ({ aliases }) => aliases.join(", "),
        cell: ({ row: { original } }) => {
          const { aliases } = original;

          const renderButton = () => (
            <IconButton
              icon={isEmptyArray(aliases) ? <AddOutlinedIcon fontSize="small" /> : <EditOutlinedIcon fontSize="small" />}
              onClick={() => openSideModal(EditModelVersionAliasModal, { modelId, aliasToVersionMap, modelVersion: original })}
            />
          );

          if (isEmptyArray(aliases)) {
            return isManageVersionAllowed ? renderButton() : CELL_EMPTY_VALUE;
          }

          return (
            <Box display="flex" gap={SPACING_1} alignItems="center" flexWrap="wrap">
              {aliases.map((alias) => (
                <LabelChip key={alias} label={alias} />
              ))}
              {isManageVersionAllowed && renderButton()}
            </Box>
          );
        }
      },
      mlModelPath({
        accessorKey: "path",
        headerMessageId: "path",
        headerDataTestId: "lbl_path",
        cell: ({ cell, row: { original } }) => {
          const path = cell.getValue();

          const renderButton = () => (
            <IconButton
              icon={path ? <EditOutlinedIcon fontSize="small" /> : <AddOutlinedIcon fontSize="small" />}
              onClick={() => openSideModal(EditModelPathModal, { modelId, modelVersion: original })}
            />
          );

          if (!path) {
            return isManageVersionAllowed ? renderButton() : CELL_EMPTY_VALUE;
          }

          return (
            <Box display="flex" alignItems="center" flexWrap="nowrap">
              <MlModelPathLabel path={cell.getValue()} />
              {isManageVersionAllowed && renderButton()}
            </Box>
          );
        }
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_tags">
            <FormattedMessage id="tags" />
          </TextWithDataTestId>
        ),
        id: "tags",
        style: {
          minWidth: "200px"
        },
        accessorFn: (originalRow) =>
          Object.entries(originalRow.tags ?? {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" "),
        cell: ({ row: { original } }) => {
          const { tags } = original;

          const renderButton = () => (
            <IconButton
              icon={isEmptyObject(tags) ? <AddOutlinedIcon fontSize="small" /> : <EditOutlinedIcon fontSize="small" />}
              onClick={() => openSideModal(EditModelVersionTagsModal, { modelId, modelVersion: original })}
            />
          );

          if (isEmptyObject(tags)) {
            return isManageVersionAllowed ? renderButton() : CELL_EMPTY_VALUE;
          }

          return (
            <Box display="flex" alignItems="center">
              <Box>
                <CollapsableTableCell maxRows={5} tags={tags} />
              </Box>
              {isManageVersionAllowed && renderButton()}
            </Box>
          );
        }
      },
      run({
        id: "run",
        getRunNumber: ({ run: { number } }) => number,
        getRunName: ({ run: { name } }) => name,
        getRunId: ({ run: { id } }) => id,
        getTaskId: ({ run: { task_id: taskId } }) => taskId,
        headerMessageId: "run",
        headerDataTestId: "lbl_run"
      })
    ],
    [isManageVersionAllowed, modelId, openSideModal, aliasToVersionMap]
  );

  return (
    <Box>
      <SubTitle>
        <FormattedMessage id="versions" />
      </SubTitle>
      {isLoading ? (
        <TypographyLoader linesCount={4} />
      ) : (
        <Table
          columns={columns}
          data={tableData}
          withSearch
          pageSize={50}
          localization={{
            emptyMessageId: "noVersions"
          }}
        />
      )}
    </Box>
  );
};

const MlModel = ({ model, isLoading = false }: MlModelProps) => {
  const navigate = useNavigate();
  const refetch = useRefetchApis();

  const { id = "", name = "", key = "", description = "", tags = {}, created_at: createdAt = 0, versions = [] } = model;

  return (
    <>
      <ActionBar
        data={{
          breadcrumbs: [
            <Link key={1} to={ML_MODELS} component={RouterLink}>
              <FormattedMessage id="models" />
            </Link>
          ],
          title: {
            text: name,
            isLoading,
            dataTestId: "lbl_model"
          },
          items: [
            {
              key: "btn-refresh",
              icon: <RefreshOutlinedIcon fontSize="small" />,
              messageId: "refresh",
              dataTestId: "btn_refresh",
              type: "button",
              action: () => refetch([GET_ML_MODEL])
            },
            {
              key: "edit",
              icon: <EditOutlinedIcon fontSize="small" />,
              messageId: "edit",
              action: () => {
                navigate(getEditMlModelUrl(id));
              },
              type: "button",
              isLoading,
              requiredActions: ["EDIT_PARTNER"],
              dataTestId: "btn_edit"
            }
          ]
        }}
      />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          {description && (
            <Box>
              <Description description={description} isLoading={isLoading} />
            </Box>
          )}
          <Box>
            <Summary name={name} modelKey={key} createdAt={createdAt} tags={tags} isLoading={isLoading} />
          </Box>
          <Box>
            <Version versions={versions} isLoading={isLoading} />
          </Box>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default MlModel;
