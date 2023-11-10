import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import CloudLabel from "components/CloudLabel";
import SubTitle from "components/SubTitle";
import { useApiData } from "hooks/useApiData";
import { isEmpty } from "utils/arrays";

const ChildrenList = ({ parentId }) => {
  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

  const childrenAccounts = cloudAccounts.filter(({ parent_id: accountParentId }) => accountParentId === parentId);

  return (
    <>
      <SubTitle>
        <FormattedMessage id="childDataSources" />
      </SubTitle>
      {isEmpty(childrenAccounts) ? (
        <Typography>
          <FormattedMessage id="noChildDataSourcesDiscovered" />
        </Typography>
      ) : (
        childrenAccounts.map(({ id, name, type }) => <CloudLabel key={id} id={id} name={name} type={type} />)
      )}
    </>
  );
};

export default ChildrenList;
