import { FormattedMessage } from "react-intl";
import { CreatePoolForm } from "components/forms/PoolForm";
import Tooltip from "components/Tooltip";
import { sliceByLimitWithEllipsis } from "utils/strings";
import BaseSideModal from "./BaseSideModal";

const MAX_POOL_NAME_LENGTH = 32;

class AddPoolModal extends BaseSideModal {
  get headerProps() {
    const isNameLong = this.payload?.parentPoolName.length > MAX_POOL_NAME_LENGTH;

    return {
      text: (
        <div>
          <FormattedMessage
            id="addPoolToTitle"
            values={{
              poolName: (
                <Tooltip title={isNameLong ? this.payload?.parentPoolName : undefined}>
                  <span>
                    {isNameLong
                      ? sliceByLimitWithEllipsis(this.payload?.parentPoolName, MAX_POOL_NAME_LENGTH)
                      : this.payload?.parentPoolName}
                  </span>
                </Tooltip>
              ),
            }}
          />
        </div>
      ),
      color: "success",
      dataTestIds: {
        title: "lbl_add_pool",
        closeButton: "bnt_close",
      },
    };
  }

  dataTestId = "smodal_add_pool";

  get content() {
    return (
      <CreatePoolForm
        parentId={this.payload?.parentId}
        onSuccess={this.closeSideModal}
        unallocatedLimit={this.payload?.unallocatedLimit}
      />
    );
  }
}

export default AddPoolModal;
