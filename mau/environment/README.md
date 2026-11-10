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
env.dupdate({"a.b.c": "value"})
env.get("a.b.c")  # "value"
env["a.b.c"]      # "value"

# Create from a nested dictionary with a namespace prefix.
env = Environment.from_dict({"aliases": {"source": {"args": {"engine": "source"}}}}, namespace="mau.parser")
# Stored as "mau.parser.aliases.source.args.engine" = "source"

# A namespace prefix returns a sub-environment.
env.get("mau.parser.aliases")  # Environment with key "source.args.engine"
```

Key methods:

- `from_dict(d, namespace)` - Create from a nested dictionary under a namespace prefix.
- `from_environment(env, namespace)` - Clone an existing environment, optionally under a namespace prefix.
- `get(key, default)` - Retrieve a value by dotted key. If the key is a namespace prefix, return a sub-environment.
- `update(other, namespace, overwrite)` - Merge another `Environment`. With `overwrite=False` existing keys are kept.
- `dupdate(d, namespace)` - Update from a dictionary (nested or with dotted keys) under a namespace.
- `asdict()` - Return the content as a nested dictionary.
- `asflatdict()` - Return the internal flat dictionary.
- `env[key]` / `env[key] = value` - Item access with dotted keys.

## How it connects

The environment is created at startup from:
1. The YAML configuration file (`-c` flag), stored under `mau`.
2. Environment files (`-e` flag), stored under `mau.envfiles`.
3. Environment variables (`-v` flag), stored under `mau.envvars`.
4. Variables defined in the Mau source (`:name:value`), stored as they are written.

It is then passed to lexers, parsers, and visitors, where it controls behaviour such as aliases, style mappings, and template paths.
