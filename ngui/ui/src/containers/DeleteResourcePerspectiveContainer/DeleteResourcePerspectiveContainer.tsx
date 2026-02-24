import DeleteResourcePerspective from "components/DeleteResourcePerspective";
import {
  OrganizationPerspectivesDocument,
  useUpdateOrganizationPerspectivesMutation,
} from "graphql/__generated__/hooks/restapi";
import { useOrganizationPerspectives } from "hooks/coreData/useOrganizationPerspectives";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { removeKey } from "utils/objects";

const DeleteResourcePerspectiveContainer = ({ perspectiveName, onCancel, onSuccess }) => {
  const { organizationId } = useOrganizationInfo();

  const { allPerspectives } = useOrganizationPerspectives();

  const [updateOrganizationPerspectives, { loading }] = useUpdateOrganizationPerspectivesMutation({
    update: (cache, { data }) => {
      cache.writeQuery({
        query: OrganizationPerspectivesDocument,
        variables: { organizationId },
        data: {
          organizationPerspectives: data.updateOrganizationPerspectives,
        },
      });
    },
  });

  const onDelete = () => {
    const newPerspectives = removeKey(allPerspectives, perspectiveName);

    return updateOrganizationPerspectives({
      variables: {
        organizationId,
        value: newPerspectives,
      },
    }).then(onSuccess);
  };

  return (
    <DeleteResourcePerspective perspectiveName={perspectiveName} onDelete={onDelete} onCancel={onCancel} isLoading={loading} />
  );
};

export default DeleteResourcePerspectiveContainer;
