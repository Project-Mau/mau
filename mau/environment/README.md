# Environment

This module manages hierarchical configuration and variable storage throughout the Mau processing pipeline.

## Overview

The `Environment` class provides a namespace-aware flat dictionary. All keys use dot notation (e.g. `mau.parser.aliases`) to represent hierarchy, and the class handles flattening nested dictionaries and nesting flat ones.

## Files

- `environment.py` - The `Environment` class.
- `helpers.py` - Utility functions `flatten_nested_dict()` and `nest_flattened_dict()` for converting between nested and flat dictionary representations.

## Key class

### `Environment`

A container for flattened variables with dot-notation access.

```python
env = Environment()
env.update({"a.b.c": "value"})
env.get("a.b.c")  # "value"

# Create from a nested dictionary with a namespace prefix.
env = Environment.from_dict({"aliases": {"source": {...}}}, namespace="mau.parser")
# Stored as "mau.parser.aliases.source" = {...}
```

Key methods:

- `from_dict(d, namespace)` - Create from a nested dictionary under a namespace prefix.
- `from_environment(env)` - Clone an existing environment.
- `get(key, default)` - Retrieve a value by dotted key.
- `update(other, overwrite)` - Merge another environment.
- `dupdate(d, namespace)` - Update from a flat dictionary under a namespace.
- `asdict()` - Return the internal flat dictionary.

## How it connects

The environment is created at startup from:
1. The YAML configuration file (`-c` flag).
2. Environment files (`-e` flag).
3. Environment variables (`-v` flag).
4. Variables defined in the Mau source (`:name:value`).

It is then passed to lexers, parsers, and visitors, where it controls behaviour such as aliases, style mappings, and template paths.
