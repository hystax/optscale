import CodeBlock from "components/CodeBlock";
import BaseSideModal from "./BaseSideModal";

class AwsAssumedRoleCredentialsModal extends BaseSideModal {
  headerProps = {
    messageId: "awsAssumedRoleCredentials",
    color: "primary",
    dataTestIds: {
      title: "lbl_aws_assumed_role_credentials",
      closeButton: "btn_close",
    },
  };

  dataTestId = "smodal_aws_assumed_role_credentials";

  get content() {
    return <CodeBlock text={this.payload?.text} />;
  }
}

export default AwsAssumedRoleCredentialsModal;
