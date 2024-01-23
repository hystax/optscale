import { useState } from "react";
import { EditPoolForm } from "components/PoolForm";
import PoolLabel from "components/PoolLabel";
import TabsWrapper from "components/TabsWrapper";
import GetAssignmentRulesContainer from "containers/GetAssignmentRulesContainer";
import PoolConstraintsContainer from "containers/PoolConstraintsContainer";
import ShareSettingsContainer from "containers/ShareSettingsContainer";
import PoolsService from "services/PoolsService";
import { EDIT_POOL_TAB_QUERY } from "urls";
import BaseSideModal from "./BaseSideModal";

export const EDIT_POOL_TABS = Object.freeze({
  GENERAL: "general",
  SHARE: "share",
  CONSTRAINTS: "constraints",
  ASSIGNMENT_RULES: "assignmentRules"
});

const EditPool = ({ onSuccess, id }) => {
  const { useGet } = PoolsService();
  const { data } = useGet();

  const allPools = [data, ...(data.children || [])];
  const info = allPools.find(({ id: poolId }) => poolId === id) || {};
  const parent = allPools.find(({ id: poolId }) => poolId === info.parent_id);
  const unallocatedLimit = parent?.unallocated_limit;

  const [activeTab, setActiveTab] = useState();
  const { id: poolId, name: poolName, purpose: poolPurpose, expenses_export_link: initialLink } = info;

  const tabs = [
    {
      title: EDIT_POOL_TABS.GENERAL,
      dataTestId: "tab_general",
      node: <EditPoolForm poolInfo={info} unallocatedLimit={unallocatedLimit} onSuccess={onSuccess} />
    },
    {
      title: EDIT_POOL_TABS.CONSTRAINTS,
      dataTestId: "tab_constraints",
      node: <PoolConstraintsContainer poolId={poolId} />
    },
    {
      title: EDIT_POOL_TABS.ASSIGNMENT_RULES,
      dataTestId: "tab_assignment",
      node: <GetAssignmentRulesContainer interactive={false} poolId={poolId} />
    },
    {
      title: EDIT_POOL_TABS.SHARE,
      dataTestId: "tab_share",
      node: <ShareSettingsContainer poolId={poolId} poolName={poolName} poolPurpose={poolPurpose} initialLink={initialLink} />
    }
  ];
  return (
    <TabsWrapper
      tabsProps={{
        tabs,
        defaultTab: EDIT_POOL_TABS.GENERAL,
        name: "pool-details",
        activeTab,
        queryTabName: EDIT_POOL_TAB_QUERY,
        handleChange: (event, value) => {
          setActiveTab(value);
        }
      }}
    />
  );
};

class EditPoolModal extends BaseSideModal {
  get headerProps() {
    const purpose = this.payload?.info.purpose;

    return {
      messageId: "edit{}",
      formattedMessageValues: {
        value: purpose ? (
          <PoolLabel
            disableLink
            type={purpose}
            name={this.payload?.info.name}
            iconProps={{ hasLeftMargin: true, color: "white" }}
          />
        ) : null
      },
      dataTestIds: {
        title: "lbl_edit_pool",
        closeButton: "bnt_close"
      }
    };
  }

  dataTestId = "smodal_edit_pool";

  get content() {
    return <EditPool id={this.payload?.id} onSuccess={this.closeSideModal} />;
  }
}

export default EditPoolModal;
