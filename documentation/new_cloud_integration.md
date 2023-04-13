# How to integrate new cloud to OptScale (checklist)

## Essential methods
### restapi

- add class for new cloud to cloud_adapter with correct BILLING_CREDS
- add new cloud type to restapi_server/models/enums.py -> CloudTypes
- add new cloud type to cloud_adapter/clouds.py -> SUPPORTED_BILLING_TYPES
- create migration for cloudaccount table to add new cloud type
- add cloud validation to cloud_adapter/<cloud_type>.py-> validate_credentials()
- update swagger for cloud_account APIs

## Resource discovery
### restapi

- (optional) add new resource types, see Generalized resource discovery | Workflow to add a new resource type:  for details
- implement discovery calls for required resource types in `cloud_adapter`
- add discovery_calls_map() to cloud adapter
- check tasks are created for new cloud type in deploy/docker_images/resource_discovery/scheduler.py
- update cloud-adapter version in resource_discovery requirements.txt
- (optional) update cloud_resource APIs + swagger

## Billing data import
### restapi

- update cloud adapter with billing/usage/pricing APIs for the new cloud

### diworker

- implement data importer in diworker/importers
- add the importer class to diworker/importers/factory.py-> REPORT_IMPORT_TYPES
- (optional) add new indexes for raw_expenses collection

## Cost map
### restapi

- add get_regions_coordinates() to cloud_adapter/clouds/<cloud_type>.py

## Metrics
### restapi

- add APIs for getting resource metrics from cloud to cloud_adapter/clouds/<cloud_type>.py -> get_metric()

### metroculus

- add getting metrics for cloud to metroculus_worker/processor.py
- add cloud type to SUPPORTED_CLOUD_TYPES in metroculus_scheduler/main.py

## Traffic expenses
### restapi

- (optional) add APIs for getting resource traffic

### diworker

- add create_traffic_processing_task() to diworker/importers/<cloud_type>.py

### trapper

- add processor for new cloud to trapper_worker/processor.py
- add cloud type to SUPPORTED_CLOUD_TYPES in trapper_scheduler/main.py

## Recommendations
### restapi

- (optional) add APIs for getting prices/flavors

### insider

- (optional) support new cloud in prices/flavors APIs + update swagger

### bumiworker

- support new cloud in recommendation and archive modules

## Recommendations cleanup scripts
### restapi

- implement cleanup scripts in rest_api_server/recommendation_cleanup_scripts/<cloud_type>
- (optional) update api handler and controller (rest_api_server/handlers/v2/cleanup_scripts.py, rest_api_server/controllers/cleanup_script.py)

## Optional
- add service credentials or other keys to etcd

### deploy

- optscale/templates/tpl/_config.tpl
- optscale/values.yaml
- update overlays in overlay/

## NGUI
- request a new logo from marketing, create a new React icon component
- add support for a new cloud type utils/constants.js
- create a new connection form components/ConnectCloudAccountForm
- add required translations
- for all the places listed above and whereever else - apply the code changes for the new type accordingly

