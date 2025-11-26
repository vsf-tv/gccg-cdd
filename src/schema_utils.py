import json
import os
import referencing
from referencing.jsonschema import DRAFT201909
from jsonschema import validate

def get_registry(schema_dir):
    """Load all schemas and return a configured registry."""
    
    def find_json_files(directory):
        json_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    json_files.append(os.path.join(root, file))
        return json_files
    
    def load_schema(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    
    resources = []
    schema_files = find_json_files(schema_dir)
    
    for schema_file in schema_files:
        schema = load_schema(schema_file)
        if "$id" in schema:
            resources.append((schema["$id"], referencing.Resource.from_contents(schema, DRAFT201909)))
    
    return referencing.Registry().with_resources(resources)


class SchemaRegistry(object):
    def __init__(self, schema_path):
        self.registry = get_registry(schema_path)
        self.registration_schema_file = os.path.join(schema_path, "registration-schema.json")
        self.configuration_schema_file = os.path.join(schema_path, "configuration-schema.json")
        self.status_schema_file = os.path.join(schema_path, "status-schema.json")

        self.registration_schema = self.load_json_file(self.registration_schema_file)
        self.configuration_schema = self.load_json_file(self.configuration_schema_file)
        self.status_schema = self.load_json_file(self.status_schema_file)

    def validate_registration_file(self, file: str):
        # Validate the registration schema against the metaschema
        payload = self.load_json_file(file)
        validate(instance=payload, schema=self.registration_schema)

        print("Registration schema is valid.")

    def validate_configuration(self, payload: dict):
        # Validate the configuration schema against the metaschema
        validate(instance=payload, schema=self.configuration_schema)

        print("Configuration schema is valid.")

    def validate_status(self, payload: dict):
        # Validate the status schema against the metaschema
        validate(instance=payload, schema=self.status_schema)
        print("Status schema is valid.")

    @staticmethod
    def load_json_file(filename):
        with open(filename, 'r') as f:
            return json.load(f)