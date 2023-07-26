import copy
import uuid
from unittest.mock import patch, ANY, call

from rest_api_server.tests.unittests.test_api_base import TestApiBase

AUTHORIZE_ACTION_METHOD = ('rest_api_server.controllers.assignment'
                           '.AssignmentController._authorize_action_for_pool')
RULE_APPLY_CONDITION_CLOUD_IS = ('rest_api_server.controllers.rule_apply.'
                                 'CloudIsCondition.match')


class TestRulesApiBase(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        self.cloud_acc_id = None
        _, self.organization = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.organization['id']
        self.user_id = self.gen_id()
        self.user2_id = self.gen_id()
        self.valid_employee = {
            'name': 'Eliot Alderson', 'auth_user_id': self.user_id
        }
        self.employee = self._create_employee(self.user_id, self.org_id,
                                              name='Eliot Alderson')
        self.employee2 = self._create_employee(self.user2_id, self.org_id)
        self.org_pool_id = self.organization['pool_id']
        self.update_default_owner_for_pool(
            self.org_pool_id, self.employee['id'])
        self.sub_pools = []
        self.sub_pools_ids = []
        for i in range(4):
            code, resp = self.client.pool_create(
                self.org_id,
                {'name': "sub_pool_%d" % i,
                 'parent_id': self.org_pool_id,
                 'default_owner_id': self.employee2['id']})
            self.assertEqual(code, 201)
            self.sub_pools.append(resp)
            self.sub_pools_ids.append(resp['id'])
        self.user3_id = self.gen_id()
        self.user4_id = self.gen_id()
        self.employee3 = self._create_employee(self.user3_id, self.org_id)
        self.employee4 = self._create_employee(self.user4_id, self.org_id)
        _, self.org2_bu = self.client.organization_create(
            {'name': "organization2"})
        self.org2_id = self.org2_bu['id']
        self.org2_pool_id = self.org2_bu['pool_id']
        self.org2_user_id = self.gen_id()
        self.org2_employee = self._create_employee(self.org2_user_id,
                                                   self.org2_id)

        self._mock_auth_user(self.user_id)
        self.user = {
            'id': self.user_id,
            'display_name': 'default',
            'email': 'email@email.com',
        }
        self.p_get_user_info.return_value = self.user
        self.p_activities_publish = patch(
            'rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()

    def _create_employee(self, user_id, organization_id, name=None):
        if not name:
            name = 'TestUser_%s' % self.gen_id()[:8]
        valid_employee = {
            'name': name,
            'auth_user_id': user_id
        }
        code, employee = self.client.employee_create(organization_id,
                                                     valid_employee)
        self.assertEqual(code, 201)
        return employee

    def _get_rules(self, original_resp=False, owner_id=None,
                   pool_id=None):
        code, rules = self.client.rules_list(
            organization_id=self.org_id, owner_id=owner_id, pool_id=pool_id)
        self.assertEqual(code, 200)
        if original_resp:
            return rules
        return rules['rules']

    @staticmethod
    def _prepare_rule_body(name, pool_id=None, owner_id=None,
                           conditions=None, active=None, priority=None):
        body = {'name': name,
                'conditions': conditions}
        if pool_id:
            body.update({'pool_id': pool_id})
        if owner_id:
            body.update({'owner_id': owner_id})
        if active is not None:
            body.update({'active': active})
        if priority is not None:
            body.update({'priority': priority})
        return body

    def _create_rule(self, name, org_id=None, pool_id="", owner_id="",
                     conditions=None, active=None, priority=None,
                     set_allowed=True):
        if not org_id:
            org_id = self.org_id
        if not conditions:
            conditions = [
                {"type": "name_starts_with", "meta_info": "name_starts_with"}
            ]
        if pool_id == "":
            pool_id = self.org_pool_id
        if owner_id == "":
            owner_id = self.employee['id']
        if set_allowed:
            _, employee = self.client.employee_get(owner_id)
            self.set_allowed_pair(employee['auth_user_id'], pool_id)
        rule_body = self._prepare_rule_body(
            name=name,
            pool_id=pool_id,
            owner_id=owner_id,
            conditions=conditions,
            active=active,
            priority=priority,
        )
        code, rule = self.client.rules_create(org_id, rule_body)
        self.assertEqual(code, 201, rule)
        return rule

    def _test_params(self, call, params, *args, required_parameters=None,
                     entities_should_exist=None):
        data = params.copy()
        unexpected_param_name = "unexpected_param"
        data[unexpected_param_name] = self.gen_id()
        code, response = call(*args, data)
        self.assertEqual(code, 400)
        self.assertTrue('Unexpected parameters' in response['error']['reason'])
        self.assertTrue(unexpected_param_name in response['error']['reason'])
        if required_parameters:
            for param in required_parameters:
                data = params.copy()
                data.pop(param)
                code, response = call(*args, data)
                self.assertEqual(code, 400)
                self.assertEqual(response['error']['reason'],
                                 '%s is not provided' % param)
        if entities_should_exist:
            for param in entities_should_exist:
                data = params.copy()
                id = str(self.gen_id())
                data[param] = id
                code, response = call(*args, data)
                self.assertEqual(code, 400)
                self.assertTrue('%s %s doesn\'t exist' % (param, id)
                                in response['error']['reason'])
                self.assertTrue(response['error']['error_code'], 'OE0212')


class TestRuleApi(TestRulesApiBase):

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_rule(self, p_authorize):
        """
        Basic create rule request flow.
        Steps:
           - 1. Check initial count of rules. Should be 0.
           - 2. Create FullPair rule.
           - 3. Verify response code is 201.
           - 4. Verify count rules is 1.
           - 12. Create rule in inactive state.
             - verify state

        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        full_rule = self._create_rule('Test rule')
        self.assertEqual(self.p_activities_publish.call_count, 1)
        self.assertEqual(full_rule['pool_name'], self.organization['name'])
        self.assertEqual(full_rule['pool_purpose'], 'business_unit')
        self.assertEqual(full_rule['owner_name'], self.employee['name'])
        self.assertEqual(full_rule['creator_name'], self.employee['name'])
        self.assertEqual(full_rule['priority'], 1)
        rules = self._get_rules()
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]['id'], full_rule['id'])
        inactive = self._create_rule("Inactive rule",
                                     active=False)
        self.assertEqual(self.p_activities_publish.call_count, 2)
        code, rule = self.client.rule_get(inactive['id'])
        self.assertEqual(code, 200)
        self.assertEqual(rule['active'], False)
        rules = self._get_rules()
        self.assertEqual(len(rules), 2)
        code, rules = self.client.rules_list(self.org_id,
                                             valid_rules_only=True)
        self.assertEqual(code, 200)
        all_rules = rules['rules']
        for rule in all_rules:
            self.assertTrue(rule['id'] != inactive['id'])
            self.assertIn('priority', rule)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_rule_with_priority(self, p_authorize):
        """
           - 1. Check initial count of rules. Should be 0.
           - 2. Create 2 rules
           - 3. Create rules with priority 2
           - 4. Get list of rules and check priorities
        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)

        rule1 = self._create_rule('rule1')
        rule3 = self._create_rule('rule3')
        self.assertEqual(self.p_activities_publish.call_count, 2)

        rules = self._get_rules()
        self.assertEqual(len(rules), 2)

        rule2 = self._create_rule('rule2', priority=2)
        self.assertEqual(self.p_activities_publish.call_count, 3)
        self.assertEqual(rule2['priority'], 2)

        rule_body = self._prepare_rule_body(
            name='rule4',
            pool_id=self.org_pool_id,
            owner_id=self.employee['id'],
            conditions=[{"type": "name_starts_with", "meta_info": "name_starts_with"}],
            active=None,
            priority=5,
        )
        code, resp = self.client.rules_create(self.org_id, rule_body)

        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

        rule_body.update({'priority': 0})

        code, resp = self.client.rules_create(self.org_id, rule_body)

        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0224')

        rules = self._get_rules()
        self.assertEqual(len(rules), 3)
        for priority, rule in enumerate(rules, start=1):
            self.assertEqual(rule['priority'], priority)

    def test_params_create_rule(self):
        """
        Test required parameters for creation rule.
        Steps:
           - 1. Verify requests without param:
             - name
             - conditions
           - 2. Verify requests with param, but entity doesn't exist:
             - owner_id
             - pool_id
           - 3. Verify request with conditions as empty array
             - err_code should be 400
             - localized code should be E0216
           - 3. Verify request without conditions in body
             - err_code should be 400
             - localized code should be E0216
           - 4. Try to create rule without owner or pool.
             - localized code should be E0216
           - 5. Try to create rule with unsupported param in condition
             - localized code should be E0212
           - 6. Try to create rule with unsupported condition type
             - localized code should be E0430
           - 7. Try to create rule with absent meta in condition
             - localized code should be E0430
           - 8. Try to create rule with absent type in condition
             - localized code should be E0430
           - 9. Try to create rule with pool in another org
             - localized code should be E0002
           - 10. Try to create rule with owner in another org
             - localized code should be E0002
           - 11. Try to create rule with invalid condition format
             - localized code should be E0344

        """
        rule_body = self._prepare_rule_body(
            name="Test rule",
            pool_id=self.org_pool_id,
            owner_id=self.employee['id'],
            conditions=[
                {"type": "name_starts_with", "meta_info": "test_"}
            ]
        )
        self._test_params(
            self.client.rules_create, rule_body, self.org_id,
            required_parameters=['name', 'conditions'],
            entities_should_exist=['owner_id', 'pool_id']
        )
        rule_body_copy = rule_body.copy()
        rule_body_copy['name'] = None
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')
        rule_body_copy = rule_body.copy()
        rule_body_copy['conditions'] = []
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')
        rule_body_copy = rule_body.copy()
        rule_body_copy.pop('conditions')
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')
        rule_body_copy = rule_body.copy()
        rule_body_copy['conditions'] = None
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')
        rule_body_copy = rule_body.copy()
        rule_body_copy['pool_id'] = None
        rule_body_copy['owner_id'] = None
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')
        rule_body_copy = rule_body.copy()
        rule_body_copy.pop('pool_id')
        rule_body_copy.pop('owner_id')
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')
        rule_body_copy = copy.deepcopy(rule_body)
        rule_body_copy['conditions'][0]['unsupported_param'] = 'test_val'
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')
        rule_body_copy = copy.deepcopy(rule_body)
        rule_body_copy['conditions'][0]['type'] = 'UNSUPPORTED_TYPE'
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0430')
        required_condition_fields = ['type', 'meta_info']
        for param in required_condition_fields:
            rule_body_copy = copy.deepcopy(rule_body)
            rule_body_copy['conditions'][0].pop(param)
            code, resp = self.client.rules_create(self.org_id,
                                                  rule_body_copy)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, 'OE0216')
        rule_body_copy = copy.deepcopy(rule_body)
        rule_body_copy['conditions'][0]['unsupported_key'] = None
        code, resp = self.client.rules_create(self.org_id,
                                              rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')
        rule_body_copy = rule_body.copy()
        rule_body_copy['owner_id'] = self.org2_employee['id']
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0005')
        rule_body_copy = rule_body.copy()
        rule_body_copy['pool_id'] = self.org2_pool_id
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0005')
        rule_body_copy = rule_body.copy()
        rule_body_copy['conditions'] = ["123", "123"]
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0344')

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_list_rules(self, p_authorize):
        """
        Test list rules API with query params
        Steps:
           - 1. Create rules:
             - rule1: full pair rule for pool_org and user1 as owner
             - rule2: full pair rule for pool_org and user2 as owner
             - rule3: full pair rule for sub_pool1 and user2 as owner
             - rule4: full pair rule for sub_pool1 and user1 as owner
           - 2. Request list rules. Should return all 4 rules
           - 3. Request list rules with owner as user1. Should return:
             - rule1, rule4
           - 4. Request list rules with pool as org_pool. Should return:
             - rule1, rule2
           - 5. Request list rules with org_pool and user1 as owner.
             Should return:
               - rule1
           -9. Request list rules with invalid owner_id.
             Should return:
               - empty array.
        """
        def check_list_rules(expected_rules, **kwargs):
            expected_ids = set([r['id'] for r in expected_rules])
            rules = self._get_rules(**kwargs)
            self.assertEqual(len(rules), len(expected_rules))
            for rule in rules:
                self.assertTrue(rule['id'] in expected_ids)

        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        rule1 = self._create_rule("rule1")
        rule2 = self._create_rule("rule2", owner_id=self.employee2['id'])
        rule3 = self._create_rule(
            "rule3", pool_id=self.sub_pools[0]['id'],
            owner_id=self.employee2['id'])
        rule4 = self._create_rule(
            "rule4", pool_id=self.sub_pools[0]['id'],
            owner_id=self.employee['id'])
        rules = self._get_rules()
        self.assertEqual(len(rules), 4)

        check_list_rules([rule1, rule4], owner_id=self.employee['id'])
        check_list_rules([rule1, rule2], pool_id=self.org_pool_id)
        check_list_rules([rule1], owner_id=self.employee['id'],
                         pool_id=self.org_pool_id)
        check_list_rules([], owner_id=self.gen_id())

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_rule_with_existing_name(self, p_authorize):
        """
        Test for trying crete rule with name that is already exist
        Steps:
           - 1. Check initial count of rules. Should be 0.
           - 2. Create FullPair rule with name TestRule.
           - 3. Verify response code is 201.
           - 4. Verify count rules is 1.
           - 5. Create FullPair rule with the same name.
             - verify localized code is E0431
           - 6. Verify count rules is still 1.
           - 5. Create rules with the same name.
             - verify localized code is E0431
           - 6. Verify count rules is still 1.

        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        rule_body = self._prepare_rule_body(
            name="TestRule",
            pool_id=self.org_pool_id,
            owner_id=self.employee['id'],
            conditions=[
                {"type": "name_starts_with", "meta_info": "test_"}
            ]
        )
        code, full_rule = self.client.rules_create(self.org_id, rule_body)
        self.assertEqual(code, 201)
        rules = self._get_rules()
        self.assertEqual(len(rules), 1)
        code, resp = self.client.rules_create(self.org_id, rule_body)
        self.assertEqual(code, 409)
        self.verify_error_code(resp, 'OE0149')
        rules = self._get_rules()
        self.assertEqual(len(rules), 1)
        p_authorize.return_value = False
        rule_body_copy = rule_body.copy()
        rule_body_copy.pop('pool_id')
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 409)
        self.verify_error_code(resp, 'OE0149')
        rules = self._get_rules()
        self.assertEqual(len(rules), 1)
        rule_body_copy = rule_body.copy()
        rule_body_copy.pop('owner_id')
        code, resp = self.client.rules_create(self.org_id, rule_body_copy)
        self.assertEqual(code, 409)
        self.verify_error_code(resp, 'OE0149')
        rules = self._get_rules()
        self.assertEqual(len(rules), 1)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_full_rule_with_invalid_target_pair(self, p_authorize):
        """
        Test creation rule with invalid target pair.
        Steps:
           - 1. Check initial count of rules. Should be 0.
           - 2. Create FullPair rule with invalid target pair.
           - 3. Verify response code is 403.
           - 4. Verify localized code is E0379
           - 4. Verify count rules is 0.

        """
        p_authorize.return_value = False
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        rule_body = self._prepare_rule_body(
            name="TestRule",
            pool_id=self.org_pool_id,
            owner_id=self.employee['id'],
            conditions=[
                {"type": "name_starts_with", "meta_info": "test_"}
            ]
        )
        code, resp = self.client.rules_create(self.org_id, rule_body)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, "OE0379")
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_rule_with_invalid_tag_is_meta(self, p_authorize):
        """
        Test creation rule with invalid tag is meta condition
        Steps:
           - 1. Try to create rule with tags_is conditions with all possible
             invalid meta_info parameter
           - 2. Verify all tries are failed
           - 3. Verify no new rule created

        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        valid_rule_body = self._prepare_rule_body(
            name="TestRule",
            pool_id=self.org_pool_id,
            owner_id=self.employee['id'],
            conditions=[
                {"type": "name_starts_with", "meta_info": "test_"}
            ]
        )

        def check_response(meta_info, error_code):
            conditions = [
                {"type": "tag_is", "meta_info": meta_info}
            ]
            valid_rule_body['conditions'] = conditions
            code, resp = self.client.rules_create(self.org_id,
                                                  valid_rule_body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, error_code)

        check_response(None, "OE0216")
        check_response(123, "OE0214")
        check_response({}, "OE0214")
        check_response("{}", "OE0216")
        check_response("123", "OE0344")
        check_response("\"123\"", "OE0344")
        check_response("{\"123\"}", "OE0219")
        check_response("{\"key\": \"key\"}", "OE0216")
        check_response("{\"key\": 123}", "OE0214")
        check_response("{\"value\": \"value\"}", "OE0216")
        check_response("{\"key\": \"key\", \"value\": 123}", "OE0214")
        check_response("{\"key\": \"k\", \"value\": \"v\", \"new\": \"value\"}",
                       "OE0212")
        check_response("{\"key\": \"key\", \"unexpected\": \"value\"}", "OE0216")
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_rule(self, p_authorize):
        """
        Basic test for rule update
        Steps:
           - 1. Check initial count of rules. Should be 0.
           - 2. Create FullPair rule with 2 conditions.
           - 3. Update rule:
             - update name
             - update active
             - update pool_id
             - update owner_id
             - delete one condition
             - update one existing condition
             - add new condition
           - 4. Verify all changes with GET rule API
           - 5. Verify extra fields in PATCH response

        """
        final_conditions_after_update = set()
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        conditions = [
            {"type": "name_starts_with", "meta_info": "NAME_STARTS_WITH"},
            {"type": "name_contains", "meta_info": "NAME_CONTAINS"},
        ]
        full_rule = self._create_rule("TestRule", conditions=conditions)
        rules = self._get_rules()
        self.assertEqual(len(rules), 1)
        code, original_rule = self.client.rule_get(full_rule['id'])
        self.assertEqual(code, 200)
        modified_rule_body = copy.deepcopy(original_rule)
        modified_rule_body['name'] = 'new_name'
        modified_rule_body['active'] = False
        modified_rule_body['owner_id'] = self.employee2['id']
        modified_rule_body['pool_id'] = self.sub_pools[0]['id']
        modified_rule_body['conditions'][0]['type'] = 'name_ends_with'
        final_conditions_after_update.add('name_ends_with')
        modified_rule_body['conditions'][0]['meta_info'] = 'NAME_ENDS_WITH'
        modified_rule_body['conditions'] = modified_rule_body['conditions'][:-1]
        modified_rule_body['conditions'].append(
            {"type": "name_is", "meta_info": "NAME_IS"})
        final_conditions_after_update.add('name_is')
        code, patched_response = self.client.rule_update(original_rule['id'],
                                                         modified_rule_body)
        self.assertEqual(code, 200)
        self.assertEqual(self.p_activities_publish.call_count, 2)
        code, modified_rule = self.client.rule_get(full_rule['id'])
        self.assertEqual(code, 200)
        self.assertEqual(modified_rule['name'], 'new_name')
        self.assertEqual(modified_rule['active'], False)
        self.assertEqual(modified_rule['pool_id'],
                         self.sub_pools[0]['id'])
        self.assertEqual(modified_rule['owner_id'], self.employee2['id'])
        self.assertEqual(len(modified_rule['conditions']), 2)
        for condition in modified_rule['conditions']:
            self.assertTrue(condition['type'] in final_conditions_after_update)
            self.assertTrue(
                condition['meta_info'].lower() in final_conditions_after_update)
        self.assertEqual(patched_response['creator_name'],
                         self.employee['name'])
        self.assertEqual(patched_response['owner_name'], self.employee2['name'])
        self.assertEqual(patched_response['pool_purpose'], "budget")
        self.assertEqual(patched_response['pool_name'],
                         self.sub_pools[0]['name'])
        for field in ["creator_name", "pool_name",
                      "owner_name", "pool_purpose"]:
            self.assertTrue(field in patched_response.keys())

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_rule_with_existing_name(self, p_authorize):
        """
        Basic test for rule update
        Steps:
           - 1. Check initial count of rules. Should be 0.
           - 2. Create two rules with names rule0 and rule1
           - 3. Create rule with name rule2
           - 4. Create rule with name rule3
           - 5. Try to update rule0 with names rule1, rule2, rule3.
             - all updates should be failed.
             - verify localized code is E0431
           - 6. Check that rule0 has the same name
           - 7. Create rule for org2 with name rule_new_org.
           - 8. Update rule0 with name rule_new_org. Should be succeeded.

        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        rule0 = self._create_rule("rule0")
        rule1 = self._create_rule("rule1")
        rule2 = self._create_rule("rule2")
        rule3 = self._create_rule("rule3")
        for name in [rule1['name'], rule2['name'], rule3['name']]:
            rule0['name'] = name
            code, resp = self.client.rule_update(rule0['id'], rule0)
            self.assertEqual(code, 409)
            self.verify_error_code(resp, 'OE0149')
        code, rule = self.client.rule_get(rule0['id'])
        self.assertEqual(code, 200)
        self.assertEqual(rule['name'], "rule0")
        new_rule_name = "rule_new_org"
        with self.switch_user(self.org2_user_id):
            self._create_rule(new_rule_name, org_id=self.org2_id,
                              owner_id=self.org2_employee['id'],
                              pool_id=self.org2_pool_id)
        rule0['name'] = new_rule_name
        code, resp = self.client.rule_update(rule0['id'],
                                             rule0)
        # 5 rules created and one updated
        self.assertEqual(self.p_activities_publish.call_count, 6)
        self.assertEqual(code, 200)
        code, rule = self.client.rule_get(rule0['id'])
        self.assertEqual(code, 200)
        self.assertEqual(rule['name'], new_rule_name)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_rule_with_invalid_tag_is_meta(self, p_authorize):
        """
        Test update rule with invalid tag is meta condition
        Steps:
           - 1. Create valid rule with tag_is condition.
           - 2. Try to update rule with tags_is conditions with all possible
             invalid meta_info parameter
           - 3. Verify all tries are failed
           - 4. Verify no new rule created

        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        conditions = [
            {
             "type": "tag_is",
             "meta_info": "{\"key\":\"key\",\"value\":\"value\"}"
             }
        ]
        rule1 = self._create_rule('rule1', conditions=conditions)
        rules = self._get_rules()
        self.assertEqual(len(rules), 1)
        valid_rule_body = self._prepare_rule_body(
            name="TestRule",
            pool_id=self.org_pool_id,
            owner_id=self.employee['id'],
            conditions=[
                {"type": "name_starts_with", "meta_info": "test_"}
            ]
        )

        def check_response(meta_info, error_code):
            conditions = [
                {"type": "tag_is", "meta_info": meta_info}
            ]
            valid_rule_body['conditions'] = conditions
            code, resp = self.client.rule_update(rule1['id'],
                                                 valid_rule_body)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, error_code)

        check_response(None, "OE0216")
        check_response(123, "OE0214")
        check_response({}, "OE0214")
        check_response("{}", "OE0216")
        check_response("123", "OE0344")
        check_response("\"123\"", "OE0344")
        check_response("{\"123\"}", "OE0219")
        check_response("{\"key\": \"key\"}", "OE0216")
        check_response("{\"key\": 123}", "OE0214")
        check_response("{\"value\": \"value\"}", "OE0216")
        check_response("{\"key\": \"key\", \"value\": 123}", "OE0214")
        check_response("{\"key\": \"k\", \"value\": \"v\", \"new\": \"value\"}",
                       "OE0212")
        check_response("{\"key\": \"key\", \"unexpected\": \"value\"}", "OE0216")
        rules = self._get_rules()
        self.assertEqual(len(rules), 1)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_rule_name_is_null(self, p_authorize):
        """
        Testing update rule name with None value
        Steps:
           - 1. Check initial count of rules. Should be 0.
           - 2. Create two FullPair rules with name rule0.
           - 3. Try to update rule0 with name is None
             - update should be failed.
             - verify localized code is E0216
           - 4. Try to update rule0 with name is integer value
             - update should be failed.
             - verify localized code is E0214

        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        full_rule = self._create_rule("rule0")
        full_rule['name'] = None
        code, resp = self.client.rule_update(full_rule['id'],
                                             full_rule)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')
        full_rule['name'] = 0
        code, resp = self.client.rule_update(full_rule['id'],
                                             full_rule)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0214')

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_get_update_rule_invalid_id(self, p_authorize):
        """
        Test get_update_rule for invalid rule id
        Steps:
           - 1. Get rule by invalid id. Verify
             - code is 404
             - localized code is E0002
           - 2. Update rule by invalid id. Verify
             - code is 404
             - localized code is E0002
           - 3. Create rule for org2
           - 4. Try to update rule in org1 for rule id from org 2

        """
        p_authorize.return_value = True
        code, resp = self.client.rule_get(self.gen_id())
        self.assertEqual(code, 404)
        self.verify_error_code(resp, "OE0002")
        code, resp = self.client.rule_update(self.gen_id(), {})
        self.assertEqual(code, 404)
        self.verify_error_code(resp, "OE0002")
        # TODO uncomment after OSB-412 is done
        # with self.switch_user(self.org2_user_id):
        #     org2_rule = self._create_rule(
        #         'new_rule_name',
        #         org_id=self.org2_id,
        #         owner_id=self.org2_employee['id'],
        #         budget_id=self.org2_budget_id)
        # org2_rule_id = org2_rule['id']
        # code, resp = self.client.rule_get(org2_rule_id)
        # self.assertEqual(code, 404)
        # self.verify_error_code(resp, "OE0002")
        # code, resp = self.client.rule_update(org2_rule_id, {})
        # self.assertEqual(code, 404)
        # self.verify_error_code(resp, "OE0002")

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_with_change_rule_priority(self, p_authorize):
        """
        Test update rule with changing rule priority
        Steps:
           - 2. Create 3 rules
           - 3. Update rule3 and set priority 1
           - 5. Verify new rule order
        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        rule1 = self._create_rule('rule1')
        rule2 = self._create_rule('rule2')
        rule3 = self._create_rule('rule3')
        rules = self._get_rules()
        self.assertEqual(len(rules), 3)
        original_order = [r['id'] for r in rules]

        rule2['priority'] = 0
        code, resp = self.client.rule_update(rule2['id'], rule2)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0224')

        rule2['priority'] = 5
        code, resp = self.client.rule_update(rule2['id'], rule2)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

        rule1['priority'] = 1
        code, _ = self.client.rule_update(rule1['id'], rule1)
        self.assertEqual(code, 200)
        rules = self._get_rules()
        self.assertEqual(len(rules), 3)
        expected_new_order = [original_order[2], original_order[0],
                              original_order[1]]
        new_order = [r['id'] for r in rules]
        self.assertEqual(expected_new_order, new_order)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_without_pool_and_owner(self, p_authorize):
        """
        Test update rule without owner and pool specified
        Steps:
           - 1. Create full pair rule
           - 2. Update rule remove owner and pool
             - verify it's failed
             - verify localized code
           - 3. Update rule (remove owner)
           - 4. Update rule (remove pool)
             - verify it's failed
             - verify localized code

        """
        p_authorize.return_value = True
        rule = self._create_rule('test rule')
        rule_tmp = copy.deepcopy(rule)
        rule_tmp['pool_id'] = None
        rule_tmp['owner_id'] = None
        code, resp = self.client.rule_update(rule['id'], rule_tmp)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0216")
        rule_tmp = copy.deepcopy(rule)
        rule_tmp['owner_id'] = None
        code, resp = self.client.rule_update(rule['id'], rule_tmp)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0216")
        rule_tmp['pool_id'] = None
        code, resp = self.client.rule_update(rule['id'], rule_tmp)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0216")

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_remove_all_conditions(self, p_authorize):
        """
        Test update rule without conditions
        Steps:
           - 1. Create full pair rule
           - 2. Update rule without conditions(empty array)
             - verify it's failed
             - verify localized code is E0216

        """
        p_authorize.return_value = True
        rule = self._create_rule('test rule')
        rule['conditions'] = []
        code, resp = self.client.rule_update(rule['id'], rule)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0216")

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_invalid_conditions(self, p_authorize):
        """
        Test update rule with invalid conditions
        Steps:
           - 1. Create full pair rule
           - 2. Update rule with
             - not supported type in condition(E0430)
             - not supported key in condition(E0212)
             - with condition type is None(E0430)
             - with condition meta is None(E0216)
             - verify all requests are failed

        """
        p_authorize.return_value = True
        rule = self._create_rule('test rule')
        tmp_rule = copy.deepcopy(rule)
        tmp_rule['conditions'][0]['type'] = "unsupported_type"
        code, resp = self.client.rule_update(rule['id'], tmp_rule)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0430")
        tmp_rule = copy.deepcopy(rule)
        tmp_rule['conditions'][0]['unsupported_key'] = "dummy"
        code, resp = self.client.rule_update(rule['id'], tmp_rule)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0212")
        tmp_rule = copy.deepcopy(rule)
        tmp_rule['conditions'][0]["type"] = None
        code, resp = self.client.rule_update(rule['id'], tmp_rule)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0430")
        tmp_rule = copy.deepcopy(rule)
        tmp_rule['conditions'][0]["meta_info"] = None
        code, resp = self.client.rule_update(rule['id'], tmp_rule)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0216")

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_invalid_target_pair(self, p_authorize):
        """
        Test update rule without owner and pool specified
        Steps:
           - 1. Create full pair rule
           - 2. Update rule with invalid target pair
             - verify it's failed
             - verify localized code is E0379

        """
        p_authorize.return_value = True
        rule = self._create_rule('test rule')
        p_authorize.return_value = False
        code, resp = self.client.rule_update(rule['id'], rule)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, "OE0379")

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_active_is_none(self, p_authorize):
        """
        Test update rule with invalid active field
        Steps:
           - 1. Create full pair rule
           - 2. Update rule with active is None
             - verify it's failed
             - verify localized code is E0212

        """
        p_authorize.return_value = True
        rule = self._create_rule('test rule')
        rule['active'] = None
        code, resp = self.client.rule_update(rule['id'], rule)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0216")

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_update_invalid_pool_or_owner_id(self, p_authorize):
        """
        Test update rule with specifying invalid owner id.
        Steps:
           - 1. Create full pair rule
           - 2. Update rule with random UUID for pool_id and owner_id
             - verify it's failed
             - verify localized code is E0002
           -3. Update rule with pool_id and owner_id from another org.

        """
        p_authorize.return_value = True
        rule = self._create_rule('test rule')
        for param in ['pool_id', 'owner_id']:
            rule_tmp = copy.deepcopy(rule)
            rule_tmp[param] = self.gen_id()
            code, resp = self.client.rule_update(rule['id'], rule_tmp)
            self.assertEqual(code, 400)
            self.verify_error_code(resp, "OE0005")
        rule_tmp = copy.deepcopy(rule)
        rule_tmp['pool_id'] = self.org2_pool_id
        code, resp = self.client.rule_update(rule['id'], rule_tmp)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0005")
        rule_tmp = copy.deepcopy(rule)
        rule_tmp['owner_id'] = self.org2_employee['id']
        code, resp = self.client.rule_update(rule['id'], rule_tmp)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, "OE0005")

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_test_patch_rule_fields(self, p_authorize):
        """
        Test update rule with field by filed
        Steps:
           - 1. Create full pair rule
           - 2. Update all fields in rule one by one using only this key in body
           - 3. Verify all fields are updated

        """
        p_authorize.return_value = True
        rule = self._create_rule('test rule')
        new_rule = {
            'name': 'new_name',
            'pool_id': self.sub_pools[0]['id'],
            'owner_id': self.employee2['id'],
            'conditions':
                [{"type": "name_ends_with", "meta_info": "name_ends_with"}]
        }
        for key in new_rule.keys():
            body = {key: new_rule[key]}
            code, resp = self.client.rule_update(rule['id'], body)
            self.assertEqual(code, 200)
            code, rule = self.client.rule_get(rule['id'])
            self.assertEqual(code, 200)
            if key == 'conditions':
                for cond in rule[key]:
                    cond.pop('id')
            self.assertEqual(rule[key], new_rule[key])

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_delete_rule(self, p_authorize):
        """
        Test delete rule
        Steps:
           - 1. Create rule rule1
           - 2. Create rule rule2
           - 3. Create rule rule3
           - 4. Verify count of rules, should be 3
           - 5. Delete rules one by one and check count -1
           - 6. Try to delete rule that is doesn't exist

        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        rule1 = self._create_rule('rule1')
        rule2 = self._create_rule('rule2')
        rule3 = self._create_rule('rule3')
        rules = self._get_rules()
        self.assertEqual(len(rules), 3)
        code, _ = self.client.rule_delete(rule1['id'])
        self.assertEqual(code, 204)
        self.assertEqual(self.p_activities_publish.call_count, 4)
        rules = self._get_rules()
        self.assertEqual(len(rules), 2)
        code, _ = self.client.rule_delete(rule2['id'])
        self.assertEqual(code, 204)
        self.assertEqual(self.p_activities_publish.call_count, 5)
        rules = self._get_rules()
        self.assertEqual(len(rules), 1)
        code, _ = self.client.rule_delete(rule3['id'])
        self.assertEqual(code, 204)
        self.assertEqual(self.p_activities_publish.call_count, 6)
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        code, resp = self.client.rule_delete(self.gen_id())
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_delete_rule_priority_change(self, p_authorize):
        """
        Test delete rule
        Steps:
           - 1. Create 3 rules
           - 2. Verify count of rules, should be 3
           - 3. Delete middle value
           - 4. Check priority order updated and have no gaps
        """
        p_authorize.return_value = True
        rules = self._get_rules()
        self.assertEqual(len(rules), 0)
        rule1 = self._create_rule('rule1')
        rule2 = self._create_rule('rule2')
        rule3 = self._create_rule('rule3')
        rules = self._get_rules()
        self.assertEqual(len(rules), 3)
        code, _ = self.client.rule_delete(rule2['id'])
        self.assertEqual(code, 204)
        rules = self._get_rules()
        self.assertEqual(len(rules), 2)
        for i, rule in enumerate(rules, start=1):
            self.assertEqual(rule['priority'], i)


class TestApplyRuleApi(TestRulesApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        patch('rest_api_server.handlers.v1.base.BaseAuthHandler.'
              '_get_user_info', return_value=self.user).start()
        aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, aws_cloud_acc, auth_user_id=self.user_id)
        _, cloud_rules = self.client.rules_list(self.org_id)
        self.set_allowed_pair(self.user_id,
                              cloud_rules['rules'][0]['pool_id'])
        self.cloud_acc_id = self.cloud_acc['id']

    def _create_resources(self, names, cloud_resource_ids=[]):
        valid_body = {'resources': []}
        for i, name in enumerate(names):
            cloud_resource_id = 'res_id_%s' % self.gen_id()
            if i < len(cloud_resource_ids):
                cloud_resource_id = cloud_resource_ids[i]
            valid_body['resources'].append(
                {
                    'cloud_resource_id': cloud_resource_id,
                    'name': name,
                    'resource_type': 'VM',
                }
            )
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc_id, valid_body, return_resources=True)
        self.assertEqual(code, 200)
        return result['resources']

    def _verify_assignments(self, resources, expected_map):
        self.assertEqual(len(resources), len(expected_map.keys()))
        for resource in resources:
            self.assertEqual(
                resource.get('employee_id'),
                expected_map[resource['name']]['employee_id'])
            self.assertEqual(
                resource.get('pool_id'),
                expected_map[resource['name']]['pool_id'])

    @patch(AUTHORIZE_ACTION_METHOD)
    @patch(RULE_APPLY_CONDITION_CLOUD_IS)
    def test_apply_rules_all_supported_conditions(self, p_rule_apply,
                                                  p_authorize):
        """
        Test checks all supported conditions in one rule
        Steps:
           - 1. Create full pair rule rule1 with:
             - name_is
             - name_starts_with
             - name_ends_with
             - name_contains
           - 2. Create resources:
             - one matched all conditions
             - one doesn't match name_is
           - 3. Verify the first resource is assigned, the second one is not.

        """
        p_authorize.return_value = True
        p_rule_apply.return_value = False
        conditions = [
            {"type": "name_starts_with", "meta_info": "starts_"},
            {"type": "name_ends_with", "meta_info": "_ends"},
            {"type": "name_contains", "meta_info": "contains"},
            {"type": "name_is", "meta_info": "starts_contains_ends"},
        ]
        self._create_rule('test_rule', conditions=conditions,
                          pool_id=self.sub_pools_ids[0],
                          owner_id=self.employee2['id'])
        resources = self._create_resources(
            ['starts_contains_ends', 'starts_contains_new_ends']
        )
        expected_map = {
            'starts_contains_ends': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': self.employee2['id']
            },
            'starts_contains_new_ends': {
                'pool_id': self.org_pool_id,
                'employee_id':  self.employee['id']
            }
        }
        self._verify_assignments(resources, expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    @patch(RULE_APPLY_CONDITION_CLOUD_IS)
    def test_apply_rules_multiple_rules_multiple_resources(self, p_rule_apply,
                                                           p_authorize):
        """
        Test checks applying rules. Multiple rules, multiple resources
        Steps:
           - 1. Create multiple rules rule1, rule2, rule3
           - 2. Create resources:
             - two resources matched rule1
             - two resources matched rule2
             - two resources matched rule3
             - two doesn't match any rules
           - 3. Verify the resource assignments.

        """
        p_authorize.return_value = True
        p_rule_apply.return_value = False
        conditions = [
            {"type": "name_starts_with", "meta_info": "starts_"},
        ]
        rule1 = self._create_rule('rule1', conditions=conditions,
                                  pool_id=self.sub_pools_ids[0],
                                  owner_id=self.employee['id'])
        conditions = [
            {"type": "name_ends_with", "meta_info": "_ends"},
        ]
        rule2 = self._create_rule('rule2', conditions=conditions,
                                  pool_id=self.sub_pools_ids[1],
                                  owner_id=self.employee2['id'])
        conditions = [
            {"type": "name_contains", "meta_info": "contains"},
        ]
        rule3 = self._create_rule('rule3', conditions=conditions,
                                  pool_id=self.sub_pools_ids[2],
                                  owner_id=self.employee3['id'])

        res_map = {
            'starts_name_1': 'cloud_resource_id_1',
            'name_2': 'starts_/res_2/id',
            'name_3_ends': 'cloud_resource_id_3',
            'name_4': 'res_4/_ends',
            'name_contains_5': 'cloud_resource_id_5',
            'name_6': 'res_id/contains_6',
            'name_7': 'res_7_id',
            'name_8': 'res_8_id'
        }
        resources = self._create_resources(
            names=list(res_map.keys()),
            cloud_resource_ids=list(res_map.values())
        )
        expected_map = {
            'starts_name_1': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': self.employee['id']
            },
            'name_2': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': self.employee['id']
            },
            'name_3_ends': {
                'pool_id': self.sub_pools_ids[1],
                'employee_id': self.employee2['id']
            },
            'name_4': {
                'pool_id': self.sub_pools_ids[1],
                'employee_id': self.employee2['id']
            },
            'name_contains_5': {
                'pool_id': self.sub_pools_ids[2],
                'employee_id': self.employee3['id']
            },
            'name_6': {
                'pool_id': self.sub_pools_ids[2],
                'employee_id': self.employee3['id']
            },
            'name_7': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'name_8': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
        }
        self._verify_assignments(resources, expected_map)
        applied_rules_map = {
            'starts_name_1': [
                {'id': rule1['id'], 'name': rule1['name'],
                 'pool_id': rule1['pool_id']}
            ],
            'name_2': [
                {'id': rule1['id'], 'name': rule1['name'],
                 'pool_id': rule1['pool_id']}
            ],
            'name_3_ends': [
                {'id': rule2['id'], 'name': rule2['name'],
                 'pool_id': rule2['pool_id']}
            ],
            'name_4': [
                {'id': rule2['id'], 'name': rule2['name'],
                 'pool_id': rule2['pool_id']}
            ],
            'name_contains_5': [
                {'id': rule3['id'], 'name': rule3['name'],
                 'pool_id': rule3['pool_id']}
            ],
            'name_6': [
                {'id': rule3['id'], 'name': rule3['name'],
                 'pool_id': rule3['pool_id']}
            ],
            'name_7': None,
            'name_8': None
        }
        for r in resources:
            name = r.get('name')
            applied_rules = applied_rules_map[name]
            self.assertEqual(applied_rules, r.get('applied_rules'))
            if applied_rules:
                self.assertEqual(
                    r.get('pool_id'), applied_rules[0]['pool_id'])

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_apply_rules_rules_priority(self, p_authorize):
        """
        Test checks applying rules by priority.
        Steps:
           - 1. Create rule1 and rule2 with conflicted conditions
           - 2. Create 4 resources matched both rules
           - 3. Verify the resource assignments.

        """
        p_authorize.return_value = True
        conditions = [
            {"type": "name_starts_with", "meta_info": "rule"},
        ]
        self._create_rule('rule1', conditions=conditions,
                          pool_id=self.sub_pools_ids[0],
                          owner_id=self.employee2['id'])
        self._create_rule('rule2', conditions=conditions,
                          pool_id=self.sub_pools_ids[1],
                          owner_id=self.employee3['id'])
        resources = self._create_resources(
            [
                'rule1',
                'rule2',
                'rule3',
                'rule4',
            ]
        )
        expected_map = {
            'rule1': {
                'pool_id': self.sub_pools_ids[1],
                'employee_id': self.employee3['id']
            },
            'rule2': {
                'pool_id': self.sub_pools_ids[1],
                'employee_id': self.employee3['id']
            },
            'rule3': {
                'pool_id': self.sub_pools_ids[1],
                'employee_id': self.employee3['id']
            },
            'rule4': {
                'pool_id': self.sub_pools_ids[1],
                'employee_id': self.employee3['id']
            }
        }
        self._verify_assignments(resources, expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    @patch(RULE_APPLY_CONDITION_CLOUD_IS)
    def test_apply_rules_no_rules(self, p_rule_apply, p_authorize):
        """
        Test checks creation resources in case of no rules are available in org
        Steps:
           - 1. Create 4 resources.
           - 2. Verify root assignments.
           - 3. Create 4 rules
           - 4. Create resource that doesn't match any rules.
           - 5. Verify root assignments.

        """
        p_authorize.return_value = True
        p_rule_apply.return_value = False
        resources = self._create_resources(
            [
                'rule1',
                'rule2',
                'rule3',
                'rule4',
            ]
        )
        expected_map = {
            'rule1': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'rule2': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'rule3': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'rule4': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            }
        }
        self._verify_assignments(resources, expected_map)
        conditions = [
            {"type": "name_starts_with", "meta_info": "rule"},
        ]
        self._create_rule('rule1', conditions=conditions,
                          pool_id=self.sub_pools_ids[0],
                          owner_id=self.employee2['id'])
        self._create_rule('rule2', conditions=conditions,
                          pool_id=self.sub_pools_ids[1],
                          owner_id=self.employee3['id'])
        resources = self._create_resources(
            [
                '_rule1',
                '_rule2',
                '_rule3',
                '_rule4',
            ]
        )
        expected_map = {
            '_rule1': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            '_rule2': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            '_rule3': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            '_rule4': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            }
        }
        self._verify_assignments(resources, expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    @patch(RULE_APPLY_CONDITION_CLOUD_IS)
    def test_apply_rules_disabled_rules(self, p_rule_apply, p_authorize):
        """
        Test checks creation resources in case disabled rules
        Steps:
           - 1. Create 2 rules rule1 and rule2.
           - 2. Create resource matched both rules
           - 3. Verify rule1 is applied
           - 4. Disable rule1
           - 5. Create resource matched both rules
           - 3. Verify rule2 is applied
           - 4. Disable rule2
           - 5. Create resource matched both rules
           - 3. Verify no rules are applied

        """
        p_authorize.return_value = True
        p_rule_apply.return_value = False
        conditions = [
            {"type": "name_starts_with", "meta_info": "rule"},
        ]
        rule1 = self._create_rule('rule1', conditions=conditions,
                                  pool_id=self.sub_pools_ids[0],
                                  owner_id=self.employee2['id'])
        rule2 = self._create_rule('rule2', conditions=conditions,
                                  pool_id=self.sub_pools_ids[1],
                                  owner_id=self.employee3['id'])
        resources = self._create_resources(
            [
                'rule2'
            ]
        )
        expected_map = {
            'rule2': {
                'pool_id': self.sub_pools_ids[1],
                'employee_id': self.employee3['id']
            }
        }
        self._verify_assignments(resources, expected_map)
        code, resp = self.client.rule_update(rule2['id'], {'active': False})
        self.assertEqual(code, 200)
        resources = self._create_resources(
            [
                'rule1'
            ]
        )
        expected_map = {
            'rule1': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': self.employee2['id']
            }
        }
        self._verify_assignments(resources, expected_map)
        code, resp = self.client.rule_update(rule1['id'], {'active': False})
        self.assertEqual(code, 200)
        resources = self._create_resources(
            [
                'rule3'
            ]
        )
        expected_map = {
            'rule3': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            }
        }
        self._verify_assignments(resources, expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_apply_rules_complex(self, p_authorize):
        """
        Test checks creation resources in case complex rules
        Steps:
           - 1. Create multiple rules with multiple condition types.
           - 2. Create resource one resource match only one rule.
           - 3. Verify assignments.

        """
        p_authorize.return_value = True

        conditions = [
            {"type": "name_starts_with", "meta_info": "qa"},
            {"type": "name_ends_with", "meta_info": "prod"},
            {"type": "name_contains", "meta_info": "resource"},
        ]
        self._create_rule('full_pair_rule1', conditions=conditions,
                          pool_id=self.sub_pools_ids[0],
                          owner_id=self.employee2['id'])
        conditions = [
            {"type": "name_is", "meta_info": "special_name"},
        ]
        self._create_rule('full_pair_rule2', conditions=conditions,
                          pool_id=self.sub_pools_ids[1],)

        resources = self._create_resources(
            [
             'qa_resource_prod',
             'qa_resource1_prod',
             'special_name',
            ]
        )
        expected_map = {
            'qa_resource_prod': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': self.employee2['id']
            },
            'qa_resource1_prod': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': self.employee2['id']
            },
            'special_name': {
                'pool_id': self.sub_pools_ids[1],
                'employee_id': self.employee['id']
            },
        }
        self._verify_assignments(resources, expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_apply_rules_tag_condition(self, p_authorize):
        """
        Test checks creation resources in case of tag condition in rule
        Steps:
           - 1. Create rule with tag_is condition rule1
           - 2. Create resources with tags matched rule1
           - 3. Verify assignment.

        """
        p_authorize.return_value = True
        conditions = [
            {
             "type": "tag_is",
             "meta_info": "{\"key\":\"key\",\"value\":\"value\"}"
             }
        ]
        self._create_rule('rule1', conditions=conditions)
        valid_body = {'resources': []}
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource',
                'resource_type': 'VM',
                'tags': {
                    "key": "value",
                    "key1": "value1",
                    "key2": "value2",
                }
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource1',
                'resource_type': 'VM',
                'tags': {
                    "key1": "value1",
                    "key": "value",
                    "key2": "value2",
                }
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource2',
                'resource_type': 'VM',
                'tags': {
                    "key1": "value1",
                    "key2": "value2",
                    "key": "value"
                }
            }
        )
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc_id, valid_body, return_resources=True)
        self.assertEqual(code, 200)
        expected_map = {
            'resource': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource1': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource2': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
        }
        self._verify_assignments(result['resources'], expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_apply_rules_tag_exists_condition(self, p_authorize):
        """
        Test checks creation resources in case of tag exists condition in rule
        Steps:
           - 1. Create rule with tag_exists condition rule1
           - 2. Create resources with tags matched rule1
           - 3. Verify assignment.

        """
        p_authorize.return_value = True
        conditions = [
            {"type": "tag_exists", "meta_info": "key"}
        ]
        self._create_rule('rule1', conditions=conditions)
        valid_body = {'resources': []}
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource',
                'resource_type': 'VM',
                'tags': {
                    "key": "value",
                    "key1": "value1",
                    "key2": "value2",
                }
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource1',
                'resource_type': 'VM',
                'tags': {
                    "key1": "value1",
                    "key": "value",
                    "key2": "value2",
                }
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource2',
                'resource_type': 'VM',
                'tags': {
                    "key1": "value1",
                    "key2": "value2",
                    "key": "value"
                }
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource3',
                'resource_type': 'VM',
                'tags': {
                    "key1": "value1",
                    "key2": "value2",
                    "key": "value3"
                }
            }
        )
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc_id, valid_body, return_resources=True)
        self.assertEqual(code, 200)
        expected_map = {
            'resource': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource1': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource2': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource3': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
        }
        self._verify_assignments(result['resources'], expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_apply_rules_environment_resources(self, p_authorize):
        p_authorize.return_value = True
        name = 'some_name'
        conditions = [
            {"type": "name_is", "meta_info": name}
        ]
        self._create_rule('rule1', conditions=conditions)
        code, res = self.environment_resource_create(
            self.org_id, {'name': name, 'resource_type': 'type'})
        self.assertEqual(code, 201)
        expected_map = {
            name: {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            }
        }
        self._verify_assignments([res], expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_apply_rules_cluster(self, p_authorize):
        p_authorize.return_value = True
        conditions = [
            {"type": "tag_exists", "meta_info": "key"}
        ]
        self._create_rule('rule1', conditions=conditions)
        valid_body = {'resources': []}
        valid_body['resources'].extend([
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource',
                'resource_type': 'VM',
                'tags': {
                    "key": "value",
                }
            },
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource1',
                'resource_type': 'VM',
                'tags': {
                    "key": "value",
                }
            }])
        code, ct = self.client.cluster_type_create(
            self.org_id, {'name': 'some', 'tag_key': 'key'})
        self.assertEqual(code, 201)
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc_id, valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        expected_map = {
            'resource': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource1': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            }
        }
        cluster = next(self.resources_collection.find(
            {'cluster_type_id': ct['id']}))
        self._verify_assignments(result['resources'], expected_map)
        self.assertEqual(cluster.get('pool_id'), self.org_pool_id)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_apply_rules_tag_value_starts_condition(self, p_authorize):
        """
        Test checks creation resources in case of tag value starts with
        condition in rule
        Steps:
           - 1. Create rule with tag_value_starts_with condition rule1
           - 2. Create resources with tags matched rule1
           - 3. Verify assignment.

        """
        p_authorize.return_value = True
        conditions = [
            {
                "type": "tag_value_starts_with",
                "meta_info": "{\"key\":\"key\",\"value\":\"value\"}"
            }
        ]
        self._create_rule('rule1', conditions=conditions)
        valid_body = {'resources': []}
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource',
                'resource_type': 'VM',
                'tags': {
                    "key": "value",
                    "key1": "value1",
                    "key2": "value2",
                }
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource1',
                'resource_type': 'VM',
                'tags': {
                    "key1": "value1",
                    "key": "value value",
                    "key2": "value2",
                }
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource2',
                'resource_type': 'VM',
                'tags': {
                    "key1": "value1",
                    "key2": "value2",
                    "key": "value vbivalue"
                }
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource3',
                'resource_type': 'VM',
                'tags': {
                    "key": "valueue",
                    "key1": "value1",
                    "key2": "value2",
                }
            }
        )
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc_id, valid_body, return_resources=True)
        self.assertEqual(code, 200)
        expected_map = {
            'resource': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource1': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource2': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource3': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
        }
        self._verify_assignments(result['resources'], expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    @patch(RULE_APPLY_CONDITION_CLOUD_IS)
    def test_apply_rules_resource_type(self, p_rule_apply, p_authorize):
        """
        Test checks creation resources in case of res type condition in rule
        Steps:
           - 1. Create rule with resource_type_is condition rule1
           - 2. Create resource with type matched rule1 and two more resource
             which are not
           - 3. Verify assignment.

        """
        p_authorize.return_value = True
        p_rule_apply.return_value = False
        conditions = [
            {"type": "resource_type_is", "meta_info": "VM"}
        ]
        self._create_rule('rule1', conditions=conditions)
        valid_body = {'resources': []}
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource',
                'resource_type': 'VM'
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource1',
                'resource_type': 'VM1'
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource2',
                'resource_type': 'vm'
            }
        )
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc_id, valid_body, return_resources=True)
        self.assertEqual(code, 200)
        expected_map = {
            'resource': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource1': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource2': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
        }
        self._verify_assignments(result['resources'], expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    @patch(RULE_APPLY_CONDITION_CLOUD_IS)
    def test_apply_rules_region(self, p_rule_apply, p_authorize):
        """
        Test checks creation resources in case of res region condition in rule
        Steps:
           - 1. Create rule with region_is condition rule1
           - 2. Create resource with type matched rule1 and two more resource
             which are not
           - 3. Verify assignment.

        """
        p_authorize.return_value = True
        p_rule_apply.return_value = False
        conditions = [
            {"type": "region_is", "meta_info": "test_region"}
        ]
        self._create_rule('rule1', conditions=conditions,
                          pool_id=self.sub_pools_ids[0],
                          owner_id=self.employee2['id'])
        valid_body = {'resources': []}
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource',
                'region': 'test_region1',
                'resource_type': 'VM'
            }
        )
        # matched resource
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource1',
                'region': 'test_region',
                'resource_type': 'VM1'
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource2',
                'region': 'test_region3',
                'resource_type': 'vm'
            }
        )
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc_id, valid_body, return_resources=True)
        self.assertEqual(code, 200)
        expected_map = {
            'resource': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource1': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': self.employee2['id']
            },
            'resource2': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
        }
        self._verify_assignments(result['resources'], expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_apply_rules_cloud_is(self, p_authorize):
        """
        Test checks creation resources in case of cloud condition in rule
        Steps:
           - 1. Create rule with cloud_is condition rule1
           - 2. Create resources for right cloud
           - 3. Verify assignment.
           - 4. Create resources for wrong cloud
           - 5. Verify assignment.
           - 6. Verify that get rules returns related cloud acc entities
        """
        p_authorize.return_value = True
        auth_user_id_1 = self.gen_id()
        _, employee1 = self.client.employee_create(
            self.org_id, {'name': 'name1', 'auth_user_id': auth_user_id_1})
        conditions = [
            {"type": "cloud_is", "meta_info": self.cloud_acc_id}
        ]
        self._create_rule('rule1', conditions=conditions,
                          pool_id=self.sub_pools_ids[0],
                          owner_id=employee1['id'])
        valid_body = {'resources': []}
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource',
                'resource_type': 'VM'
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource1',
                'resource_type': 'VM1'
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource2',
                'resource_type': 'vm'
            }
        )
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc_id, valid_body, return_resources=True)
        self.assertEqual(code, 200)
        expected_map = {
            'resource': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': employee1['id']
            },
            'resource1': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': employee1['id']
            },
            'resource2': {
                'pool_id': self.sub_pools_ids[0],
                'employee_id': employee1['id']
            },
        }
        self._verify_assignments(result['resources'], expected_map)
        aws_cloud_acc1 = {
            'name': 'my cloud_acc1',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }

        _, cloud_acc1 = self.create_cloud_account(
            self.org_id, aws_cloud_acc1, auth_user_id=auth_user_id_1)
        cloud_acc_id = cloud_acc1['id']
        valid_body = {'resources': []}
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource',
                'resource_type': 'VM'
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource1',
                'resource_type': 'VM1'
            }
        )
        valid_body['resources'].append(
            {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': 'resource2',
                'resource_type': 'vm'
            }
        )
        code, result = self.cloud_resource_create_bulk(
            cloud_acc_id, valid_body, return_resources=True)
        self.assertEqual(code, 200)

        expected_map = {
            'resource': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource1': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
            'resource2': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            },
        }
        self._verify_assignments(result['resources'], expected_map)
        code, rules = self.client.rules_list(
            organization_id=self.org_id)
        self.assertEqual(code, 200)
        self.assertIn(self.cloud_acc_id, rules['entities'])

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_apply_rules_with_deleted_condition(self, p_authorize):
        """
        Test checks that deleted conditions don't apply on filtering.
        Steps:
           - 1. Create rule with one condition.
           - 2. Modify rule. Add one new condition, remove existing one.
           - 3. Create resource matches to the new condition,
             but doesn't match to the deleted one.
           - 3. Verify assignments.

        """
        p_authorize.return_value = True
        conditions = [
            {"type": "name_starts_with", "meta_info": "qa"}
        ]
        rule = self._create_rule('full_pair_rule1', conditions=conditions)
        conditions = [
            {"type": "name_starts_with", "meta_info": "prod"}
        ]
        code, patched_response = self.client.rule_update(
            rule['id'],
            {'conditions': conditions}
        )
        resources = self._create_resources(
            [
             'prod_resource_prod',
            ]
        )
        expected_map = {
            'prod_resource_prod': {
                'pool_id': self.org_pool_id,
                'employee_id': self.employee['id']
            }
        }
        self._verify_assignments(resources, expected_map)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_rule_prioritize(self, p_authorize):
        p_authorize.return_value = True

        for rule_name in ['rule1', 'rule2', 'rule3', 'rule4']:
            conditions = [{"type": "name_starts_with", "meta_info": rule_name}]
            self._create_rule(rule_name, conditions=conditions)

        code, rules = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        initial_rule_order = [r['id'] for r in rules['rules']]
        # prioritize third rule
        expected_new_order = [initial_rule_order[2], initial_rule_order[0],
                              initial_rule_order[1], initial_rule_order[3],
                              initial_rule_order[4]]
        code, response = self.client.rule_prioritize(initial_rule_order[2])
        self.assertEqual(code, 200)
        new_order = [r['id'] for r in response['rules']]
        self.assertEqual(expected_new_order, new_order)

        code, list_response = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(list_response, response)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_rule_prioritize_first(self, p_authorize):
        p_authorize.return_value = True

        for rule_name in ['rule1', 'rule2', 'rule3', 'rule4']:
            conditions = [{"type": "name_starts_with", "meta_info": rule_name}]
            self._create_rule(rule_name, conditions=conditions)

        code, rules = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        initial_rule_order = [r['id'] for r in rules['rules']]
        code, response = self.client.rule_prioritize(initial_rule_order[0])
        self.assertEqual(code, 200)
        new_order = [r['id'] for r in response['rules']]
        self.assertEqual(initial_rule_order, new_order)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_rule_promote(self, p_authorize):
        p_authorize.return_value = True

        for rule_name in ['rule1', 'rule2', 'rule3', 'rule4']:
            conditions = [{"type": "name_starts_with", "meta_info": rule_name}]
            self._create_rule(rule_name, conditions=conditions)

        code, rules = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        initial_rule_order = [r['id'] for r in rules['rules']]

        # promote fourth rule
        expected_new_order = [initial_rule_order[0], initial_rule_order[1],
                              initial_rule_order[3], initial_rule_order[2], initial_rule_order[4]]
        code, resp = self.client.rule_promote(initial_rule_order[0])
        self.assertEqual(code, 200)

        code, response = self.client.rule_promote(initial_rule_order[3])
        self.assertEqual(code, 200)

        new_order = [r['id'] for r in response['rules']]
        self.assertEqual(expected_new_order, new_order)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_rule_demote(self, p_authorize):
        p_authorize.return_value = True

        for rule_name in ['rule1', 'rule2', 'rule3', 'rule4']:
            conditions = [{"type": "name_starts_with", "meta_info": rule_name}]
            self._create_rule(rule_name, conditions=conditions)

        code, rules = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        initial_rule_order = [r['id'] for r in rules['rules']]

        # demote first rule
        expected_new_order = [initial_rule_order[1], initial_rule_order[0],
                              initial_rule_order[2], initial_rule_order[4],
                              initial_rule_order[3]]
        code, resp = self.client.rule_demote(initial_rule_order[3])
        self.assertEqual(code, 200)

        code, response = self.client.rule_demote(initial_rule_order[0])
        self.assertEqual(code, 200)

        new_order = [r['id'] for r in response['rules']]
        self.assertEqual(expected_new_order, new_order)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_rule_deprioritize(self, p_authorize):
        p_authorize.return_value = True

        for rule_name in ['rule1', 'rule2', 'rule3', 'rule4']:
            conditions = [{"type": "name_starts_with", "meta_info": rule_name}]
            self._create_rule(rule_name, conditions=conditions)

        code, rules = self.client.rules_list(self.org_id)
        self.assertEqual(code, 200)
        initial_rule_order = [r['id'] for r in rules['rules']]

        # deprioritize second rule
        expected_new_order = [initial_rule_order[0], initial_rule_order[2],
                              initial_rule_order[3], initial_rule_order[4],
                              initial_rule_order[1]]
        code, response = self.client.rule_deprioritize(initial_rule_order[1])

        self.assertEqual(code, 200)
        new_order = [r['id'] for r in response['rules']]
        self.assertEqual(expected_new_order, new_order)

    @patch(AUTHORIZE_ACTION_METHOD)
    @patch(RULE_APPLY_CONDITION_CLOUD_IS)
    def test_invalid_rule_deactivated(self, p_rule_apply, p_authorize):
        p_authorize.return_value = True
        p_rule_apply.return_value = False
        m_activities_publish = patch(
            'rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()
        conditions = [
            {"type": "name_starts_with", "meta_info": "prod"}
        ]
        rule = self._create_rule('rule1', conditions=conditions,
                                 pool_id=self.sub_pools_ids[2],
                                 owner_id=self.employee3['id'],
                                 set_allowed=False)
        resources = self._create_resources(['prod_resource_prod'])
        code, rule = self.client.rule_get(rule['id'])
        self.assertEqual(code, 200)
        self.assertFalse(rule['active'])
        m_activities_publish.assert_has_calls([
            call(rule['organization_id'], rule['id'], 'rule',
                 'rule_deactivated', ANY, 'rule.rule_deactivated',
                 add_token=True)])

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_name_conditions_case_insensitive(self, p_authorize):
        p_authorize.return_value = True
        code, pool = self.client.pool_create(self.org_id, {'name': 'test_pool'})
        for condition_name in ['name_is', 'name_contains', 'name_starts_with',
                               'name_ends_with']:
            expected_map = {
                condition_name: {'pool_id': pool['id'],
                                 'employee_id': self.employee['id']}}
            conditions = [{"type": condition_name,
                           "meta_info": condition_name.upper()}]
            self._create_rule(name=condition_name, conditions=conditions,
                              pool_id=pool['id'])
            resources = {'resources': [{
                'name': condition_name,
                'cloud_resource_id': str(uuid.uuid4()),
                'resource_type': 'test'
            }]}
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc_id, resources, return_resources=True)
            self.assertEqual(code, 200)
            self._verify_assignments(result['resources'], expected_map)


class TestRulesApplyApi(TestRulesApiBase):
    def setUp(self, version='v2'):
        super().setUp()
        self._mock_auth_user(self.user_id)
        patch('rest_api_server.handlers.v1.base.BaseAuthHandler._get_user_info',
              return_value=self.user).start()
        patch(AUTHORIZE_ACTION_METHOD, return_value=True).start()
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, aws_cloud_acc, auth_user_id=self.user_id)
        _, cloud_acc_rule = self.client.rules_list(self.org_id)
        self.cloud_acc_rule = cloud_acc_rule['rules'][0]
        self.cloud_acc_id = self.cloud_acc['id']

    def _create_resources(self, names, pool_id=None, employee_id=None,
                          tags=None):
        valid_body = {'resources': []}
        for name in names:
            resource_dict = {
                'cloud_resource_id': 'res_id_%s' % self.gen_id(),
                'name': name,
                'resource_type': 'VM',
            }
            if not pool_id:
                pool_id = self.org_pool_id
            if not employee_id:
                employee_id = self.employee['id']
            resource_dict['pool_id'] = pool_id
            resource_dict['employee_id'] = employee_id
            if tags:
                resource_dict['tags'] = tags
            valid_body['resources'].append(resource_dict)
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc_id, valid_body, return_resources=True)
        self.assertEqual(code, 200)
        return result['resources']

    def test_rules_apply_api_invalid_params(self):
        code, resp = self.client.rules_apply(self.org_id, pool_id=1)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0214')

        code, resp = self.client.rules_apply(self.org_id, pool_id='  ')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0416')

        code, resp = self.client.rules_apply(self.org_id, pool_id='')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0215')

        code, resp = self.client.rules_apply(self.org_id, pool_id='a' * 500)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0215')

        code, resp = self.client.rules_apply(
            self.org_id, pool_id=self.org_pool_id, include_children='a')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0226')

        body_unexpected = {'pool_id': self.org_pool_id, 'aa': 'bb'}
        code, resp = self.client.post(self.client.rules_apply_url(self.org_id),
                                      body_unexpected)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

    def verify_assignment(self, resource_id, pool_id, employee_id):
        code, resource = self.client.cloud_resource_get(resource_id)
        self.assertEqual(code, 200)
        self.assertEqual(resource['pool_id'], pool_id)
        self.assertEqual(resource['employee_id'], employee_id)

    def test_rules_apply_api_include_children(self):
        sub_pool_id = self.sub_pools[0]['id']
        code, sub_sub_pool = self.client.pool_create(
            self.org_id,
            {'name': "sub_sub_pool",
             'parent_id': sub_pool_id})
        self.assertEqual(code, 201)
        sub_sub_pool_id = sub_sub_pool['id']

        # root pool
        resources2 = self._create_resources(
            ['my_2', 'm3'], pool_id=self.org_pool_id,
            employee_id=self.employee['id'])
        # sub pool
        resources3 = self._create_resources(
            ['my_3', 'm4'], pool_id=sub_pool_id,
            employee_id=self.employee['id'])
        # sub sub pool
        resources4 = self._create_resources(
            ['my_4', 'm5'], pool_id=sub_sub_pool_id,
            employee_id=self.employee['id'])

        conditions = [
            {"type": "name_starts_with", "meta_info": "my_"}
        ]
        self._create_rule('rule1', conditions=conditions, set_allowed=True)

        # only processing resources from root
        code, resp = self.client.rules_apply(self.org_id,
                                             pool_id=self.org_pool_id)
        self.assertEqual(code, 201)
        self.assertEqual(resp['processed'], 2)
        self.assertEqual(resp['updated_assignments'], 1)
        self.verify_assignment(resources2[0]['id'], self.org_pool_id,
                               self.employee['id'])
        self.verify_assignment(
            resources2[1]['id'], self.cloud_acc_rule['pool_id'],
            self.employee['id'])

        # processing resources from sub and sub sub
        code, resp = self.client.rules_apply(
            self.org_id, pool_id=sub_pool_id, include_children=True)
        self.assertEqual(code, 201)
        self.assertEqual(resp['processed'], 4)
        self.assertEqual(resp['updated_assignments'], 4)
        self.verify_assignment(resources3[0]['id'], self.org_pool_id,
                               self.employee['id'])
        self.verify_assignment(
            resources3[1]['id'], self.cloud_acc_rule['pool_id'],
            self.employee['id'])
        self.verify_assignment(resources4[0]['id'], self.org_pool_id,
                               self.employee['id'])
        self.verify_assignment(
            resources4[1]['id'], self.cloud_acc_rule['pool_id'],
            self.employee['id'])

    def test_reapply_deleted_rule(self):
        self._create_resources(['my_1'])
        rule = self._create_rule('rule1', conditions=[
            {"type": "name_starts_with", "meta_info": "m"}
        ], set_allowed=True)
        code, _ = self.client.rules_apply(self.org_id,
                                          pool_id=self.org_pool_id)
        self.assertEqual(code, 201)
        self.client.rule_delete(rule['id'])
        rule2 = self._create_rule('rule2', conditions=[
            {"type": "name_starts_with", "meta_info": "my_"}
        ], pool_id=self.sub_pools_ids[0], set_allowed=True)

        m_activities_publish = patch(
            'rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()
        code, _ = self.client.rules_apply(
            self.org_id, pool_id=self.org_pool_id)
        self.assertEqual(code, 201)
        m_activities_publish.assert_has_calls([
            call(self.org_id, self.org_id, 'organization',
                 'rules_processing_started', ANY,
                 'organization.rules_processing_started', add_token=True),
            call(self.org_id, rule2['id'], 'rule',
                 'rule_applied', ANY, 'rule.rule_applied', add_token=True),
            call(self.org_id, self.org_id, 'organization',
                 'rules_processing_completed', ANY,
                 'organization.rules_processing_completed', add_token=True),
        ])

    def test_rules_apply_api_clusters(self):
        m_activities_publish = patch(
            'rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()

        code, c_type = self.client.cluster_type_create(
            self.org_id, {'name': 'c_type', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        resources = self._create_resources(['my_1', 'm2'], tags={'tn': 'tv'})

        conditions = [
            {"type": "tag_exists", "meta_info": "tn"}
        ]
        rule = self._create_rule('rule1', conditions=conditions,
                                 set_allowed=True)

        code, resp = self.client.rules_apply(self.org_id, self.org_pool_id)

        m_activities_publish.assert_has_calls([
            call(self.org_id, self.org_id, 'organization',
                 'rules_processing_started', ANY,
                 'organization.rules_processing_started', add_token=True),
            call(self.org_id, rule['id'], 'rule',
                 'rule_applied', ANY, 'rule.rule_applied', add_token=True),
            call(self.org_id, self.org_id, 'organization',
                 'rules_processing_completed', ANY,
                 'organization.rules_processing_completed', add_token=True),
        ])

        self.assertEqual(code, 201)
        self.assertEqual(resp['processed'], 1)
        self.assertEqual(resp['updated_assignments'], 0)
        self.verify_assignment(resources[0]['cluster_id'], self.org_pool_id,
                               self.employee['id'])
        self.verify_assignment(resources[0]['id'], self.org_pool_id,
                               self.employee['id'])
        self.verify_assignment(resources[1]['id'], self.org_pool_id,
                               self.employee['id'])
