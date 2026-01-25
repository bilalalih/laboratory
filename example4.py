#!/usr/bin/env python3
import argparse
import json
import sys
from jsonschema import validate, ValidationError, SchemaError

# Define a simple JSON Schema for validation
# You can modify this schema to match your expected JSON structure
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "age"],
    "additionalProperties": False
}

def read_and_validate_json(file_path):
    """Reads a JSON file and validates it against the schema."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}", file=sys.stderr)
        sys.exit(1)

    # Validate JSON against schema
    try:
        validate(instance=data, schema=JSON_SCHEMA)
    except ValidationError as e:
        print(f"Validation Error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except SchemaError as e:
        print(f"Schema Error: {e.message}", file=sys.stderr)
        sys.exit(1)

    return data

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="Harry Potter",
        description="Read and validate a JSON file against a schema, then print it."
    )
    p.add_argument(
        "json_file",
        help="Path to the JSON file to read and validate."
    )
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    # Process the file
    json_data = read_and_validate_json(args.json_file)

    # Pretty print the JSON
    print(json.dumps(json_data, indent=4))

if __name__ == "__main__":
    main()
