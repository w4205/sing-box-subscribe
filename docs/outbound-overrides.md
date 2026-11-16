# Template outbound overrides

Templates may include an `outbound_overrides` array. Overrides run after subscription parsing and before selector expansion. The extension is removed from the generated sing-box configuration.

```json
{
  "outbound_overrides": [
    {
      "type": "hysteria2",
      "tag_regex": "^Example HY2$",
      "remove": ["up_mbps", "down_mbps"]
    },
    {
      "type": "vless",
      "tag_regex": "^Example REALITY$",
      "set": {"detour": "REALITY Upstream"}
    }
  ]
}
```

Each rule must match exactly one node using its protocol type and a case-sensitive tag regular expression. Missing or ambiguous matches fail generation. `remove` deletes top-level fields if present; `set` assigns top-level fields. Removing both HY2 bandwidth fields allows sing-box to use BBR. Explicit values from a subscription or parser defaults are both removed.

Templates without overrides keep their existing behavior. Templates must not contain node credentials. A relay's upstream selector must exclude the relay itself and other nodes that could route back into it.

Run unit and template integration tests with:

```text
python -m unittest discover -s tests -v
```
