import unittest

import main
import tool


class TemplateOverridesTests(unittest.TestCase):
    def test_groups_expand_after_node_overrides(self):
        main.providers = {}
        config = {
            'dns': {'servers': []},
            'outbound_overrides': [
                {'type': 'hysteria2', 'tag_regex': 'RN-',
                 'remove': ['up_mbps', 'down_mbps'],
                 'set': {'tag': 'RN HY2 Direct'}},
                {'type': 'vless', 'tag_regex': r'(?:^|\s)RN REALITY$',
                 'set': {'tag': 'RN REALITY', 'detour': 'RN REALITY Upstream'}},
            ],
            'outbounds': [
                {'type': 'direct', 'tag': 'direct'},
                {'type': 'selector', 'tag': 'RN Exit',
                 'outbounds': ['RN HY2 Direct', 'RN REALITY'],
                 'default': 'RN HY2 Direct'},
                {'type': 'selector', 'tag': 'RN REALITY Upstream',
                 'outbounds': ['direct', '{all}'], 'default': 'direct',
                 'filter': [{'action': 'exclude',
                             'keywords': [r'^RN(?:-|\s)']}]},
                {'type': 'selector', 'tag': 'All', 'outbounds': ['{all}']},
            ],
        }
        data = {'nodes': [
            {'tag': 'RN-source', 'type': 'hysteria2', 'up_mbps': 10,
             'down_mbps': 100},
            {'tag': tool.rename('RN REALITY'), 'type': 'vless'},
            {'tag': 'Osaka example', 'type': 'shadowsocks'},
            {'tag': 'Another example', 'type': 'vless'},
        ]}
        result = main.combin_to_config(config, data)
        nodes = {n['tag']: n for n in result['outbounds']}
        self.assertEqual(nodes['RN REALITY Upstream']['outbounds'],
                         ['direct', 'Osaka example', 'Another example'])
        self.assertNotIn('RN-source', nodes['All']['outbounds'])
        self.assertIn('RN HY2 Direct', nodes['All']['outbounds'])
        self.assertNotIn('up_mbps', nodes['RN HY2 Direct'])
        self.assertNotIn('down_mbps', nodes['RN HY2 Direct'])
        self.assertEqual(nodes['RN REALITY']['detour'], 'RN REALITY Upstream')
        self.assertNotIn('outbound_overrides', result)
        self.assertNotIn('filter', nodes['RN REALITY Upstream'])


if __name__ == '__main__':
    unittest.main()
