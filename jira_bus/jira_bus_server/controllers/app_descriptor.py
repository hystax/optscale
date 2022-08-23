import logging

from jira_bus_server.constants import backend_urls, frontend_urls, APP_KEY
from jira_bus_server.controllers.base import (BaseController,
                                              BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)


class AppDescriptorController(BaseController):
    APP_NAME = 'Hystax OptScale for Jira'
    APP_SHORT_NAME = 'OptScale'
    APP_DESCRIPTION = 'Manage your IT environments in Jira issues'
    ISSUE_PANEL_NAME = 'IT environments (OptScale)'
    COMMON_CONDITIONS = [{
        # Do not show environment stuff to anonymous users without Jira account
        'condition': 'user_is_logged_in'
    }]

    def app_descriptor(self, base_host=None):
        return {
            'name': self.APP_NAME,
            'description': self.APP_DESCRIPTION,
            'key': APP_KEY,
            'apiVersion': 1,
            'baseUrl': 'https://{base_host}'.format(
                base_host=base_host or self._config.public_ip(),
            ),
            'vendor': {
                'name': 'Hystax, Inc.',
                'url': 'https://hystax.com',
            },
            'authentication': {
                'type': 'jwt',
            },
            'scopes': [
                'READ',
            ],
            'lifecycle': {
                'installed': backend_urls.installed,
            },
            'modules': {
                'configurePage': {
                    'key': 'configure',
                    'url': frontend_urls.configure,
                    'name': {
                        'value': self.APP_SHORT_NAME,
                    }
                },
                'postInstallPage': {
                    'key': 'post-install',
                    'url': frontend_urls.configure,
                    'name': {
                        'value': self.APP_SHORT_NAME,
                    }
                },
                'generalPages': [{
                    'key': 'settings',
                    'url': frontend_urls.configure,
                    'name': {
                        'value': '{} Settings'.format(self.APP_SHORT_NAME),
                    },
                    'icon': {
                        'width': 16,
                        'height': 16,
                        'url': frontend_urls.app_logo_icon,
                    },
                    'conditions': self.COMMON_CONDITIONS,
                }],
                'webPanels': [{
                    'key': 'old-issue-left-panel',
                    'location': 'atl.jira.view.issue.left.context',
                    'url': frontend_urls.issue_left_panel,
                    'name': {
                        'value': self.ISSUE_PANEL_NAME,
                    },
                    'conditions': self.COMMON_CONDITIONS,
                }],
                'jiraIssueContents': [{
                    'key': 'issue-quick-button',
                    'icon': {
                        'width': 24,
                        'height': 24,
                        'url': frontend_urls.app_logo_icon,
                    },
                    'content': {
                        'type': 'label',
                        'label': {
                            'value': self.APP_SHORT_NAME
                        }
                    },
                    'tooltip': {
                        'value': self.APP_SHORT_NAME
                    },
                    'name': {
                        'value': self.ISSUE_PANEL_NAME,
                    },
                    'target': {
                        'type': 'web_panel',
                        'url': frontend_urls.issue_left_panel
                    },
                    'conditions': self.COMMON_CONDITIONS
                }],
                'webhooks': [
                    {
                        'event': 'jira:issue_updated',
                        'url': backend_urls.issue_updated
                    },
                    {
                        'event': 'jira:issue_deleted',
                        'url': backend_urls.issue_deleted
                    },
                ],
            },
            # https://developer.atlassian.com/cloud/jira/platform/connect-api-migration/
            # https://developer.atlassian.com/cloud/jira/platform/connect-active-api-migrations/
            'apiMigrations': {
                'context-qsh': True,
                'signed-install': True,
            }
        }


class AppDescriptorAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AppDescriptorController
