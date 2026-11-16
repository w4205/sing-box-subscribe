import re


def apply_outbound_overrides(config, data):
    rules = config.pop('outbound_overrides', [])
    if not rules:
        return
    nodes = [node for group in data.values() for node in group]
    for rule in rules:
        matches = [node for node in nodes
                   if node.get('type') == rule['type']
                   and re.search(rule['tag_regex'], node.get('tag', ''))]
        if len(matches) != 1:
            raise ValueError('Outbound override must match exactly one node')
        node = matches[0]
        for field in rule.get('remove', []):
            node.pop(field, None)
        node.update(rule.get('set', {}))
    tags = [node['tag'] for node in nodes]
    if len(tags) != len(set(tags)):
        raise ValueError('Outbound overrides produced duplicate node tags')
