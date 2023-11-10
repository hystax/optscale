import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import WrapperCard from "components/WrapperCard";
import DataUnderProcessing from "./Steps/DataUnderProcessing";
import ProvideData from "./Steps/ProvideData";
import RunAudit from "./Steps/RunAudit";

const getActionBarDefinition = ({ step, onCancelApplication, isLoadingProps = {} }) => ({
  title: {
    messageId: "technicalAuditReportTitle",
    dataTestId: "lbl_technical_audit"
  },
  items: [
    {
      key: "cancelApplication",
      dataTestId: "btn_cancel_application",
      icon: <CancelOutlinedIcon fontSize="small" />,
      messageId: "technicalAudit.cancelApplication",
      type: "button",
      action: onCancelApplication,
      isLoading: Object.values(isLoadingProps).some(Boolean),
      show: step === 1
    }
  ]
});

const getActiveStep = ({ step, dataSources, hasDataSourcesInProcessing, onUpdateApplication, isLoadingProps = {} }) =>
  ({
    0: <RunAudit onRunAudit={onUpdateApplication} isLoadingProps={isLoadingProps} />,
    1: (
      <ProvideData
        onNext={onUpdateApplication}
        isLoadingProps={isLoadingProps}
        dataSources={dataSources}
        hasDataSourcesInProcessing={hasDataSourcesInProcessing}
      />
    ),
    2: <DataUnderProcessing />
    // TODO: handle loading when step is still empty on refresh)
  })[step] ?? <RunAudit onRunAudit={onUpdateApplication} isLoadingProps={isLoadingProps} />;

const TechnicalAudit = (props) => (
  <>
    <ActionBar data={getActionBarDefinition(props)} />
    <PageContentWrapper>
      <WrapperCard>{getActiveStep(props)}</WrapperCard>
    </PageContentWrapper>
  </>
);

export default TechnicalAudit;
