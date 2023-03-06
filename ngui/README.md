## Environment

### Node and npm

Actual versions:

- nodejs: 16.13.2
- npm: 8.1.2

Source: https://nodejs.org/en/download/releases/

### Environment variables

These environment variables are used for setting third party services 
credentials and other application parameters.

Evironment variables file is `.env`. Please use contents of `.env.sample` as a
draft when you start development or building Docker image.

| Name                                | Description                           |
| ----------------------------------- | ------------------------------------- |
| REACT_APP_PROXY                     | Destination to proxy API requests to  |
| REACT_APP_GOOGLE_OAUTH_CLIENT_ID    | OAuth Client ID to auth via Google    |
| REACT_APP_MICROSOFT_OAUTH_CLIENT_ID | OAuth Client ID to auth via Microsoft |
| REACT_APP_GOOGLE_MAP_API_KEY        | Google Map API key                    |
| REACT_APP_GANALYTICS_ID             | Google Analytics tracking code (ID)   |
| REACT_APP_HOTJAR_ID                 | Hotjar ID                             |

### Deployment

- Staging - `integration` branch
- Production - `master` branch

## Quick start

### Configuring environment and running a local development server

1. Define `REACT_APP_PROXY` environment variable in your local environment file
2. Run
   - `npm ci && npm start` <br>
     or
   - `npm run start:ci`
3. Celebrate 🥳

### Running and Debugging

Ensure that your development server is running (`npm start`).
In VSCode: go to Debug -> Start Debugging(or Start Without Debugging) -> Select Chrome(launch.json file is already configured).

To run a "production" build locally

- define environment variables
- npm run build
- node server.js

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.<br>
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br>
You will also see any lint errors in the console.

### `npm run start:ci`

This command installs packages using `npm ci` and then runs `npm start`

### `npm run storybook`

Runs a Storybook on the default 9009 port.<br>
Open [http://localhost:9009](http://localhost:9009) to view it in the browser.

### `npm run storybook:build`

Exporting Storybook as a Static App.<br>

### `npm test`

Launches the test runner in the interactive watch mode.<br>
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run test:ci`

Launches the test runner in the CI watch mode.<br>

### `npm run build`

Builds the app for production to the `build` folder.<br>
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br>
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (Webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

### `npm run create:component {component_name}`

Create a folder with a set of files in the `src/components` folder. Each file will be pre-filled with some code according to the specified template (can be found in «tools»).

Usage: `npm run create:component MyComponent`

It will create the following files:

- `src/components/MyComponent`
- `index.js`
- `MyComponent.js`
- `MyComponent.styles.js`
- `MyComponent.test.js`

### `npm run create:container {container_name}`

Create a folder with a set of files in the `src/containers` folder. Each file will be pre-filled with some code according to the specified template (can be found in «tools»).

Usage: `npm run create:container MyContainer`

It will create the following files:

- `src/containers/MyComponent`
  - `index.js`
  - `MyContainer.js`

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: https://facebook.github.io/create-react-app/docs/code-splitting

### Analyzing the Bundle Size

This section has moved here: https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size

### Making a Progressive Web App

This section has moved here: https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app

### Advanced Configuration

This section has moved here: https://facebook.github.io/create-react-app/docs/advanced-configuration

### Deployment

This section has moved here: https://facebook.github.io/create-react-app/docs/deployment

### Linting

Install a ESLint extension for VSCode (https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)

### `npm run build` fails to minify

This section has moved here: https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify

### 'npx prettier --check "src/\*_/_.js"'

When you want to check if your files are formatted, you can run Prettier with the --check flag (or -c). This will output a human-friendly message and a list of unformatted files, if any.

### 'npx prettier --write "src/\*_/_.js"'

This rewrites all processed files in place. This is comparable to the eslint --fix workflow.

### redux-devtools-extension (https://github.com/zalmoxisus/redux-devtools-extension)

To use the tool, an extension for your browser should be installed; open the developers console and click on a Redux tab.
