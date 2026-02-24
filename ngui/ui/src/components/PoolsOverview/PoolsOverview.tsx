import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import Grid from "@mui/material/Grid";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import PoolsTable from "components/PoolsTable";
import PoolTypeIcon from "components/PoolTypeIcon";
import Tooltip from "components/Tooltip";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ASSIGNMENT_RULES } from "urls";
import { POOL_TYPE_BUSINESS_UNIT } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { sliceByLimitWithEllipsis } from "utils/strings";
import Summary from "./Summary";

const MAX_POOL_NAME_LENGTH = 64;

const PoolsOverview = ({ data, isLoading = false, isDataReady = false, isGetPoolAllowedActionsLoading = false }) => {
  const { name } = useOrganizationInfo();

  const isNameLong = name.length > MAX_POOL_NAME_LENGTH;

  const actionBarDefinition = {
    title: {
      text: (
        <Tooltip title={isNameLong ? name : undefined}>
          <span>{isNameLong ? sliceByLimitWithEllipsis(name, MAX_POOL_NAME_LENGTH) : name}</span>
        </Tooltip>
      ),
      logo: {
        icon: <PoolTypeIcon fontSize="medium" type={POOL_TYPE_BUSINESS_UNIT} hasRightMargin dataTestId="img_type" />,
      },
      dataTestId: "lbl_pool_name",
    },
    items: [
      {
        key: "configureAssignmentRules",
        icon: <AssignmentOutlinedIcon fontSize="small" />,
        messageId: "configureAssignmentRules",
        link: ASSIGNMENT_RULES,
        type: "button",
        dataTestId: "btn_configure_assignment_rules",
      },
    ],
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_2}>
          <Grid item>
            <Summary data={data} isLoading={isLoading} />
          </Grid>
          <Grid item xs={12}>
            <PoolsTable
              rootPool={data}
              isLoadingProps={{ isGetPoolLoading: isLoading, isGetPoolDataReady: isDataReady, isGetPoolAllowedActionsLoading }}
            />
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

export default PoolsOverview;
