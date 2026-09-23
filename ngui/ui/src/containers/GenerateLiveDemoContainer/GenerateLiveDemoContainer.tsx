import { useCallback, useEffect, useState } from "react";
import { Box, Stack } from "@mui/system";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { getLiveDemo, createLiveDemo } from "api";
import { GET_LIVE_DEMO, CREATE_LIVE_DEMO } from "api/restapi/actionTypes";
import GenerateLiveDemo from "components/GenerateLiveDemo/GenerateLiveDemo";
import Logo from "components/Logo";
import { initialize } from "containers/InitializeContainer/redux";
import { useCreateTokenMutation } from "graphql/__generated__/hooks/auth";
import { reset } from "reducers/route";
import { HOME, NEXT_QUERY_PARAMETER_NAME } from "urls";
import { isError } from "utils/api";
import { SPACING_6 } from "utils/layouts";
import macaroon from "utils/macaroons";
import { getSearchParams } from "utils/network";
import { createLiveDemoSelectors } from "./utils";

type GenerateLiveDemoContainerProps = {
  email?: string;
  subscribeToNewsletter?: boolean;
};

const GenerateLiveDemoContainer = ({ email, subscribeToNewsletter }: GenerateLiveDemoContainerProps) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [hasError, setHasError] = useState(false);

  const [isLoading, setIsLoading] = useState(false);

  const [createToken, { loading: loginLoading }] = useCreateTokenMutation({
    onCompleted: (data) => {
      const caveats = macaroon.processCaveats(macaroon.deserialize(data.token.token).getCaveats());
      dispatch(initialize({ ...data.token, caveats }));
    },
  });

  const retryHandler = () => {
    // Reset the state to clear all existing data, including the token.
    dispatch(reset());
    setHasError(false);
  };

  const redirectToOptscale = useCallback(() => {
    const { [NEXT_QUERY_PARAMETER_NAME]: next } = getSearchParams() as {
      [NEXT_QUERY_PARAMETER_NAME]: string;
    };
    navigate(next || HOME);
  }, [navigate]);

  useEffect(() => {
    if (hasError) {
      return;
    }

    const activeLiveDemo = async (_, getState) => {
      setIsLoading(true);
      const selectors = createLiveDemoSelectors(getState);

      try {
        await dispatch(getLiveDemo());
        if (isError(GET_LIVE_DEMO, getState())) {
          throw new Error("Failed to get live demo");
        }

        const isAlive = selectors.getIsAlive();
        if (isAlive) {
          return redirectToOptscale();
        }

        // Clear the storage from "real" organization data and prevent from calling APIs with a "real" scope id.
        // This will not redirect users back to login, this page is allowed without a token.
        await dispatch(reset());

        await dispatch(createLiveDemo({ email, subscribeToNewsletter }));
        if (isError(CREATE_LIVE_DEMO, getState())) {
          throw new Error("Failed to create live demo");
        }

        const generatedEmail = selectors.getEmail();
        const generatedPassword = selectors.getPassword();
        if (!generatedEmail || !generatedPassword) {
          throw new Error("Missing credentials");
        }

        await createToken({ variables: { email: generatedEmail, password: generatedPassword } });

        const { token } = getState()?.initial ?? {};

        if (!token) {
          throw new Error("No token");
        }

        redirectToOptscale();
      } catch {
        setHasError(true);
      } finally {
        setIsLoading(false);
      }
    };

    dispatch(activeLiveDemo);
  }, [createToken, dispatch, email, hasError, redirectToOptscale, subscribeToNewsletter]);

  return (
    <Stack spacing={SPACING_6} alignItems="center">
      <Box>
        <Logo width={200} dataTestId="img_logo" />
      </Box>
      <GenerateLiveDemo isLoading={isLoading || loginLoading} hasError={hasError} retry={retryHandler} />
    </Stack>
  );
};

export default GenerateLiveDemoContainer;
