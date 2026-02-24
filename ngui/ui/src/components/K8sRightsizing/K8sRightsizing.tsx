import ActionBar from "components/ActionBar";
import K8sRightsizingTable from "components/K8sRightsizingTable";
import PageContentDescription from "components/PageContentDescription/PageContentDescription";
import PageContentWrapper from "components/PageContentWrapper";

const K8sRightsizing = ({ actionBarDefinition, namespaces, isLoading = false, tableActionBarDefinition }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <K8sRightsizingTable namespaces={namespaces} isLoading={isLoading} tableActionBarDefinition={tableActionBarDefinition} />
      <PageContentDescription
        position="bottom"
        alertProps={{
          messageId: "k8sRightsizingDescription",
        }}
      />
    </PageContentWrapper>
  </>
);

export default K8sRightsizing;
