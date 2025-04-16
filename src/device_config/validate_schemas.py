import json
import os
from jsonschema import validate, FormatChecker
from jsonschema import Draft201909Validator

# Running this file validates the schemas and example messages.
# If the schemas and example messages are valid, the file will exit with a 0 status code.
# If the schemas and example messages are invalid, the file will exit with a 1 status code.


print("Validating schemas and example messages...")

current_directory = os.path.dirname(__file__)
template_schema_file = os.path.join(current_directory, "template_schema.json")
instance_schema_file = os.path.join(current_directory, "instance_schema.json")
example_status_file = os.path.join("../", "application_reference", "example_status.json")
example_config_file = os.path.join("../", "application_reference", "example_config.json")

with open(template_schema_file, "r") as f:
    template_schema = json.loads(f.read())

with open(instance_schema_file, "r") as f:
    instance_schema = json.loads(f.read())

with open(example_status_file, "r") as f:
    status_message = json.loads(f.read())

with open(example_config_file, "r") as f:
    config_message = json.loads(f.read())

try:
    # This will validate that your schema is a valid JSON Schema
    Draft201909Validator.check_schema(template_schema)
    print("template Schema is valid")
except Exception as e:
    print("template Schema is invalid:", e)
    exit(1)


try:
    # This will validate that your schema is a valid JSON Schema
    Draft201909Validator.check_schema(instance_schema)
    print("Client Schema is valid")
except Exception as e:
    print("Client Schema is invalid:", e)
    exit(1)

try:
    # This will validate status message against the template schema
    validate(instance=status_message, schema=template_schema, format_checker=FormatChecker())
    print("Status Message is valid for the template schema")
except Exception as e:
    print("Status Message is invalid:", e)
    exit(1)

try:
    # This will validate config message against the template schema
    validate(instance=config_message, schema=template_schema, format_checker=FormatChecker())
    print("Config Message is valid for the template schema")
except Exception as e:
    print("Status Message is invalid:", e)
    exit(1)

try:
    # This will validate status message against the instance schema
    validate(instance=status_message, schema=instance_schema, format_checker=FormatChecker())
    print("Status Message is valid for the instance schema")
except Exception as e:
    print("Status Message is invalid:", e)
    exit(1)

try:
    # This will validate config message against the instance schema
    validate(instance=config_message, schema=instance_schema, format_checker=FormatChecker())
    print("Config Message is valid for the instance schema")
except Exception as e:
    print("Status Message is invalid:", e)
    exit(1)


