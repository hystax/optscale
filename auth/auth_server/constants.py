class Urls:
    url_prefix = '/auth'

    urls_map = {
        'tokens': r"%s/tokens",
        'users_collection': r"%s/users",
        'users': r"%s/users/(?P<user_id>[^/]+)",
        'user_existence': r"%s/user_existence",
        'roles_collection': r"%s/roles",
        'roles': r"%s/roles/(?P<role_id>[^/]+)",
        'authorize': r"%s/authorize",
        'assignments_collection': r"%s/users/(?P<user_id>[^/]+)/assignments",
        'assignments': r"%s/users/(?P<user_id>[^/]+)/assignments/"
                       r"(?P<assignment_id>[^/]+)",
        'my_assignments': r"%s/assignments",
        'types_collection': r"%s/types",
        'types': r"%s/types/(?P<type_id>[^/]+)",
        'scopes': r"%s/scopes",
        'allowed_actions': r"%s/allowed_actions",
        'digests': r"%s/digests",
        'action_resources': r"%s/action_resources",
        'authorize_userlist': r"%s/authorize_userlist",
        'purposed_roles': r"%s/purposed_roles",
        'assignment_register':
            r"%s/users/(?P<user_id>[^/]+)/assignment_register",
        'user_roles': r"%s/user_roles",
        'user_action_resources':
            r"%s/users/(?P<user_id>[^/]+)/action_resources",
        'bulk_action_resources': r"%s/bulk_action_resources",
        'signin': r"%s/signin",
        'verification_codes': r"%s/verification_codes"
    }

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class UrlsV2(Urls):
    url_prefix = '/auth/v2'


urls_v2 = UrlsV2()
