import { useFormContext } from "react-hook-form";
import Dropzone from "components/Dropzone/Dropzone";
import {
  AccessKeyId,
  AccessKeySecretKey,
  AccessKeyTitle,
  AuthorizedKeyId,
  AuthorizedKeyPrivateKey,
  AuthorizedKeyTitle,
  ServiceAccountId,
  FIELD_NAMES
} from "components/NebiusConfigFormElements";
import { readFileAsText } from "utils/files";

const NebiusCredentials = () => {
  const { setValue } = useFormContext();

  const handleFileChange = async (file) => {
    if (file) {
      try {
        const credentials = JSON.parse(await readFileAsText(file));
        setValue(FIELD_NAMES.SERVICE_ACCOUNT_ID, credentials.service_account_id);
        setValue(FIELD_NAMES.KEY_ID, credentials.id);
        setValue(FIELD_NAMES.PRIVATE_KEY, credentials.private_key);
      } catch (error) {
        console.error("Error parsing JSON file", error);
      }
    }
  };

  return (
    <>
      <AuthorizedKeyTitle />
      <div
        style={{
          display: "flex",
          flexWrap: "wrap-reverse",
          justifyContent: "center",
          gap: 8
        }}
      >
        <div
          style={{
            width: "70%",
            flexGrow: 1
          }}
        >
          <ServiceAccountId />
          <AuthorizedKeyId />
          <AuthorizedKeyPrivateKey />
        </div>
        <div
          style={{
            flexGrow: 1
          }}
        >
          <Dropzone messageId="fillFromAuthorizedKeyJson" acceptedFiles={["application/json"]} onChange={handleFileChange} />
        </div>
      </div>
      <AccessKeyTitle />
      <AccessKeyId />
      <AccessKeySecretKey />
    </>
  );
};

export default NebiusCredentials;
