## Development

### Prerequisites

Ensure you have pnpm installed globally on your machine. You can install it using the following command:

```
npm install -g pnpm
```

### Workspace Structure

This is a monorepo with two packages managed using pnpm workspaces:

- `server/` - GraphQL server with Apollo Server
- `ui/` - React application with Vite

### Quick Start

#### 1. Install Dependencies

From the root directory, install all dependencies for both packages:

```
pnpm install
```

#### 2. Environment Setup

Set up environment variables for both packages:

- Copy `server/.env.sample` to `server/.env` and configure server variables
- Copy `ui/.env.sample` to `ui/.env` and configure UI variables

See the Environment section below for more details.

#### 3. Development Mode

To start both the server and UI in development mode with automatic code generation:

```
pnpm dev
```

This command will:

- Start the server in development mode (with automatic restart via nodemon)
- Start the UI development server (Vite)
- Run GraphQL code generation in watch mode
- Automatically restart services when files change

### Available Scripts

All scripts can be run from the root directory and will execute across the workspace:

#### Development

- `pnpm dev` - Start both server and UI in development mode with code generation watching
- `pnpm start` - Start both server (built) and UI (development server)

#### Building

- `pnpm build` - Build both server and UI for production

#### Code Quality

- `pnpm check` - Run linting and validation checks across all packages
- `pnpm fix` - Fix linting issues and format code across all packages

#### Code Generation

- `pnpm codegen` - Generate GraphQL types and resolvers
- `pnpm codegen:watch` - Generate GraphQL types in watch mode

### Individual Package Development

If you need to work on a specific package only:

#### Server (from `server/` directory)

- `pnpm dev` - Start server in development mode
- `pnpm start` - Build and serve the server
- `pnpm build` - Build server

#### UI (from `ui/` directory)

- `pnpm dev` - Start UI development server
- `pnpm start` - Start UI development server (alias for dev)
- `pnpm build` - Build UI for production
- `pnpm start:ci` - Install dependencies and start (for CI environments)

### Serving the UI from the Server

The server can serve the built UI version. This is useful when you only need to develop the server part:

#### 1. Build the UI:

```
cd ui
pnpm build
```

#### 2. Set the Environment Variable:

In your `server/.env` file, define the `UI_BUILD_PATH` to point to the UI build directory:

```
UI_BUILD_PATH=/path/to/ui/build
```

#### 3. Start the Server:

```
cd server
pnpm start
```

## Environment

### Node and pnpm Versions

Required versions (defined in root package.json):

- Node.js: 22.16.0
- pnpm: 10.33.0

### Environment Variables

Environment configuration files:

- `server/.env.sample` - Server environment variables template
- `ui/.env.sample` - UI environment variables template

Copy these files without the `.sample` extension and configure the values according to your setup.

**Important Security Note**: In production or dockerized environments, the server starts with `prepare-and-run.sh` script, which creates `/ui/build/config.js` where **all** `VITE_` variables (even unused ones) will be listed **with** their names. Do not store sensitive information in `VITE_` variables in `ui/.env`.

## Code Quality and Testing

### Root Level Quality Scripts

- `pnpm check` - Run linting and validation checks across all packages
- `pnpm fix` - Fix linting issues and format code across all packages

### UI Package Features

- ESLint for code linting
- Prettier for code formatting
- TypeScript type checking
- Vitest for testing
- Translation validation
- Storybook for component development

#### Available Quality Scripts (from `ui/` directory)

- `pnpm lint` - Run ESLint
- `pnpm lint:fix` - Fix ESLint issues
- `pnpm type:check` - TypeScript type checking
- `pnpm test` - Run tests
- `pnpm test:ci` - Run tests in CI mode
- `pnpm translate:check` - Check translation formatting
- `pnpm translate:fix` - Fix translation formatting
- `pnpm translate:sort` - Sort translation keys
- `pnpm storybook` - Start Storybook
- `pnpm storybook:build` - Build Storybook

### Fixing npm Module Vulnerabilities

To check and fix npm module vulnerabilities using pnpm:

#### 1. Basic vulnerability check:

```
pnpm audit
```

#### 2. Simple fixes:

To automatically fix direct vulnerabilities where possible:

```
pnpm audit --fix
```

#### 3. Handling indirect dependencies:

1. Identify the vulnerable package:

```
pnpm audit
pnpm why <package_name>
```

2. Examine package.json files to determine acceptable version ranges according to semver rules

3. Run the fix command to generate an override:

```
pnpm audit --fix
```

4. Verify the generated override follows semver rules

5. Install dependencies with the override:

```
pnpm install
```

6. After verifying the fix works, remove the override from package.json
