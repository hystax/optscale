import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import PlayCircleOutlineOutlinedIcon from "@mui/icons-material/PlayCircleOutlineOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import { Link, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { GET_ML_RUNSETS, GET_ML_RUNSET_TEMPLATE } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import { useRefetchApis } from "hooks/useRefetchApis";
import { getMlEditRunsetTemplateUrl, getMlRunsetConfigurationUrl, ML_RUNSET_TEMPLATES } from "urls";
import { SPACING_2 } from "utils/layouts";
import { RunsetsTable, Summary, Details } from "./Components";

const MlRunsetTemplate = ({
  runsetTemplate,
  isGetRunsetTemplateLoading,
  isGetRunsetsLoading,
  runsets,
  runsCount = 0,
  totalCost = 0,
  lastRunsetCost = 0
}) => {
  const refetch = useRefetchApis();

  const {
    id,
    name,
    budget,
    name_prefix: resourceNamePrefix,
    tags = {},
    hyperparameters = {},
    cloud_accounts: dataSources = [],
    tasks = [],
    instance_types: instanceTypes = [],
    regions = []
  } = runsetTemplate;

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_RUNSET_TEMPLATES} component={RouterLink}>
        <FormattedMessage id="runsetTemplatesTitle" />
      </Link>
    ],
    title: {
      isLoading: isGetRunsetTemplateLoading,
      text: name,
      dataTestId: "lbl_ml_runsets"
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_RUNSET_TEMPLATE, GET_ML_RUNSETS])
      },
      {
        key: "launch",
        icon: <PlayCircleOutlineOutlinedIcon />,
        messageId: "launch",
        link: getMlRunsetConfigurationUrl(id),
        type: "button",
        isLoading: isGetRunsetTemplateLoading,
        requiredActions: ["EDIT_PARTNER"]
      },
      {
        key: "edit",
        icon: <EditOutlinedIcon />,
        messageId: "edit",
        type: "button",
        link: getMlEditRunsetTemplateUrl(id),
        isLoading: isGetRunsetTemplateLoading,
        requiredActions: ["EDIT_PARTNER"]
      }
    ]
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            <Summary
              runsCount={runsCount}
              lastRunsetExpenses={lastRunsetCost}
              totalExpenses={totalCost}
              isLoading={isGetRunsetsLoading}
            />
          </div>
          <div>
            <Details
              tasks={tasks}
              dataSources={dataSources}
              regions={regions}
              instanceTypes={instanceTypes}
              maximumRunsetBudget={budget}
              resourceNamePrefix={resourceNamePrefix}
              tags={tags}
              hyperparameters={hyperparameters}
              isLoading={isGetRunsetTemplateLoading}
            />
          </div>
          <div>
            <RunsetsTable isLoading={isGetRunsetsLoading} runsets={runsets} />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default MlRunsetTemplate;
