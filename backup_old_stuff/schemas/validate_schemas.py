import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from schema_utils import get_registry
from jsonschema import Draft201909Validator, FormatChecker

# Enhanced build script with reference resolution
def resolve_refs(schema, all_schemas):
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref_path = schema["$ref"].replace("#/", "").replace("/", "_")
            return all_schemas.get(ref_path, schema)
        return {k: resolve_refs(v, all_schemas) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [resolve_refs(item, all_schemas) for item in schema]
    return schema

def main(tests):
    current_directory = os.path.dirname(__file__)
    
    def load_json_file(filename):
        filepath = os.path.join(current_directory, filename)
        with open(filepath, 'r') as f:
            return json.load(f)
    
    registry = get_registry(os.path.dirname(__file__))
    
    for test_name, test_config in tests.items():
        print(f"\n=== Running {test_name} ===")
        
        try:
            main_schema = load_json_file(test_config["main_schema"])
            example_data = load_json_file(test_config["example_data"])
            
            validator = Draft201909Validator(main_schema, registry=registry, format_checker=FormatChecker())
            errors = list(validator.iter_errors(example_data))
            
            if errors:
                print(f"❌ {test_name} validation failed with {len(errors)} error(s):")
                for i, error in enumerate(errors, 1):
                    path = '.'.join(str(p) for p in error.absolute_path) if error.absolute_path else 'root'
                    print(f"  {i}. {error.message} (at: {path})")
            else:
                print(f"✅ {test_name} validation successful")
                
        except Exception as e:
            print(f"❌ {test_name} validation error: {e}")

    return 0

tests = {
    "test1": {
        "main_schema": "registration-schema.json",
        "schema_directory": ".",
        "example_data": "../payloads/1_channel_encoder/registration.json"
    },
    "test2": {
        "main_schema": "configuration-schema.json",
        "schema_directory": ".",
        "example_data": "../payloads/1_channel_encoder/configuration.json"
    },
    "test3": {
        "main_schema": "status-schema.json",
        "schema_directory": ".",
        "example_data": "../payloads/1_channel_encoder/status.json"
    },
    "test4": {
        "main_schema": "registration-schema.json",
        "schema_directory": ".",
        "example_data": "../payloads/2_channel_encoder/registration.json"
    },
    "test5": {
        "main_schema": "configuration-schema.json",
        "schema_directory": ".",
        "example_data": "../payloads/2_channel_encoder/configuration.json"
    },
    "test6": {
        "main_schema": "status-schema.json",
        "schema_directory": ".",
        "example_data": "../payloads/2_channel_encoder/status.json"
    }
}

if __name__ == "__main__":
    exit(main(tests))