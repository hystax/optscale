import BaseLayout from "layouts/BaseLayout";

const MainLayout = ({ children, mainMenu }) => (
  <BaseLayout showOrganizationSelector showMainMenu mainMenu={mainMenu}>
    {children}
  </BaseLayout>
);

export default MainLayout;
