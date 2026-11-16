import copy
import unittest

from outbound_overrides import apply_outbound_overrides


class OutboundOverridesTests(unittest.TestCase):
    def setUp(self):
        self.data = {'subscription': [
            {'tag': 'RN-source', 'type': 'hysteria2', 'up_mbps': 70,
             'down_mbps': 183, 'password': 'test-only'},
            {'tag': 'RN REALITY', 'type': 'vless', 'uuid': 'test-only'},
            {'tag': 'Other HY2', 'type': 'hysteria2', 'up_mbps': 10,
             'down_mbps': 100},
        ]}
        self.config = {'outbound_overrides': [
            {'type': 'hysteria2', 'tag_regex': 'RN-',
             'remove': ['up_mbps', 'down_mbps'],
             'set': {'tag': 'RN HY2 Direct'}},
            {'type': 'vless', 'tag_regex': '^RN REALITY$',
             'set': {'detour': 'RN REALITY Upstream'}},
        ]}

    def test_bbr_relay_and_unrelated_node(self):
        other = copy.deepcopy(self.data['subscription'][2])
        apply_outbound_overrides(self.config, self.data)
        hy2, reality, unchanged = self.data['subscription']
        self.assertEqual(hy2, {'tag': 'RN HY2 Direct', 'type': 'hysteria2',
                               'password': 'test-only'})
        self.assertEqual(reality['detour'], 'RN REALITY Upstream')
        self.assertEqual(unchanged, other)
        self.assertNotIn('outbound_overrides', self.config)

    def test_missing_node_fails(self):
        self.data['subscription'].pop(0)
        with self.assertRaises(ValueError):
            apply_outbound_overrides(self.config, self.data)

    def test_ambiguous_node_fails(self):
        self.data['subscription'].append(
            {'tag': 'RN-other', 'type': 'hysteria2'})
        with self.assertRaises(ValueError):
            apply_outbound_overrides(self.config, self.data)

    def test_existing_bbr_node(self):
        node = self.data['subscription'][0]
        del node['up_mbps'], node['down_mbps']
        apply_outbound_overrides(self.config, self.data)
        self.assertNotIn('up_mbps', node)
        self.assertNotIn('down_mbps', node)

    def test_renaming_collision_fails(self):
        self.data['subscription'][2]['tag'] = 'RN HY2 Direct'
        with self.assertRaises(ValueError):
            apply_outbound_overrides(self.config, self.data)

    def test_no_overrides_preserves_nodes(self):
        expected = copy.deepcopy(self.data)
        apply_outbound_overrides({}, self.data)
        self.assertEqual(self.data, expected)


if __name__ == '__main__':
    unittest.main()
