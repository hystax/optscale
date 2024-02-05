APP_KEY = "com.optscale.integration.jira"


class BackendUrls:
    url_prefix = "/jira_bus/v2"

    app_descriptor = f"{url_prefix}/app_descriptor"
    installed = f"{url_prefix}/installed"
    issue_updated = f"{url_prefix}/issue_updated"
    issue_deleted = f"{url_prefix}/issue_deleted"
    user_assignment = f"{url_prefix}/user_assignment"
    organization_assignment = f"{url_prefix}/organization_assignment"
    organization_collection = f"{url_prefix}/organization"
    issue_info = f"{url_prefix}/issue_info"
    authorize = f"{url_prefix}/authorize"
    shareable_resource = f"{url_prefix}/shareable_resource"
    issue_attachment_collection = (
        f"{url_prefix}/shareable_resource/(?P<resource_id>[^/]+)/issue_attachment"
    )
    issue_attachment_item = f"{url_prefix}/issue_attachment/(?P<attachment_id>[^/]+)"
    shareable_book_collection = (
        f"{url_prefix}/shareable_resource/(?P<resource_id>[^/]+)/shareable_book"
    )
    shareable_book_item = f"{url_prefix}/shareable_book/(?P<booking_id>[^/]+)"
    organization_status = f"{url_prefix}/organization/(?P<organization_id>[^/]+)/status"


class FrontendUrls:
    url_prefix = "/jira_ui"

    issue_left_panel = f"{url_prefix}/issue_left_panel/"
    configure = f"{url_prefix}/configure/"
    app_logo_icon = f"{url_prefix}/icons/logo.png"


backend_urls = BackendUrls()
frontend_urls = FrontendUrls()
