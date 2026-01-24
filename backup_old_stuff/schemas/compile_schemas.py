import json
from pathlib import Path
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012
import argparse

def build_resolved_schemas(schema_folder):
    schema_dir = Path(schema_folder).resolve()

    # Load all schemas
    all_schemas = {}
    for json_file in schema_dir.rglob("*.json"):
        with open(json_file) as f:
            schema_data = json.load(f)

        rel_path = json_file.relative_to(schema_dir)
        uri = str(rel_path).replace('\\', '/')
        all_schemas[uri] = schema_data
        
        # Also store by filename for direct references
        all_schemas[json_file.name] = schema_data


    # Simple recursive resolution without registry
    def resolve_refs(schema, base_schemas):
        if isinstance(schema, dict):
            if "$ref" in schema:
                ref = schema["$ref"]
                if "#" in ref:
                    file_part, fragment = ref.split("#", 1)
                    # Handle relative paths like "definitions/primitives.json"
                    if file_part:
                        # Try exact match first
                        if file_part in base_schemas:
                            target = base_schemas[file_part]
                        # Try just the filename if full path doesn't work
                        elif file_part.split('/')[-1] in base_schemas:
                            target = base_schemas[file_part.split('/')[-1]]
                        else:
                            # Replace external reference with internal reference
                            return {"$ref": f"#{fragment}"}
                        
                        # Navigate fragment path and return the resolved content
                        try:
                            for part in fragment.strip("/").split("/"):
                                if part:
                                    target = target[part]
                            return resolve_refs(target, base_schemas)
                        except KeyError:
                            # Replace with internal reference if path exists in defs
                            return {"$ref": f"#{fragment}"}
                    elif not file_part:  # Internal reference like "#/$defs/something"
                        target = schema
                        try:
                            for part in fragment.strip("/").split("/"):
                                if part:
                                    target = target[part]
                            return resolve_refs(target, base_schemas)
                        except KeyError:
                            return schema  # Keep unresolved if path doesn't exist
                elif ref in base_schemas:
                    return resolve_refs(base_schemas[ref], base_schemas)
                return schema  # Keep unresolved refs

            return {k: resolve_refs(v, base_schemas) for k, v in schema.items()}
        elif isinstance(schema, list):
            return [resolve_refs(item, base_schemas) for item in schema]
        return schema

    # Resolve top-level schemas and merge all $defs
    result = {}
    for file_path in schema_dir.glob("*.json"):
        schema_name = file_path.stem
        uri = file_path.name
        if uri in all_schemas:
            resolved_schema = resolve_refs(all_schemas[uri], all_schemas)
            
            # Collect all $defs from all schemas
            all_defs = {}
            for schema_uri, schema_data in all_schemas.items():
                if isinstance(schema_data, dict) and "$defs" in schema_data:
                    all_defs.update(schema_data["$defs"])
            
            # Add collected $defs to the resolved schema
            if "$defs" not in resolved_schema:
                resolved_schema["$defs"] = {}
            resolved_schema["$defs"].update(all_defs)
            
            result[schema_name] = resolved_schema

    return result

def main(source_schemas_folder, dest_folder):
    # Usage
    resolved_schemas = build_resolved_schemas(source_schemas_folder)
    keys = resolved_schemas.keys()
    print(f"Resolved schemas: {resolved_schemas}")
    print(f"keys: {resolved_schemas.keys()}")
    found_count = 0
    for schema_name in ["status-schema", "registration-schema", "configuration-schema"]:
        if schema_name in keys:
            print(f"Schema {schema_name} found in the resolved schemas.")
            found_count += 1
        else:
            print(f"Schema {schema_name} NOT found in the resolved schemas.")
    
    print(f"Found {found_count} out of 3 expected schemas.")

    # Post-process to replace external references with internal ones
    def replace_external_refs(obj):
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                if "#" in ref and not ref.startswith("#"):
                    # Extract just the fragment part for internal reference
                    fragment = ref.split("#", 1)[1]
                    obj["$ref"] = f"#{fragment}"
            return {k: replace_external_refs(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_external_refs(item) for item in obj]
        return obj

    # Write the 3 resolved schemas in destinations folder
    for schema_name in ["status-schema", "registration-schema", "configuration-schema"]:
        if schema_name in keys:
            try:
                # Post-process to fix external references
                processed_schema = replace_external_refs(resolved_schemas[schema_name])
                output_path = f"{dest_folder}/{schema_name}.json"
                with open(output_path, "w") as f:
                    json.dump(processed_schema, f, indent=2)
                print(f"Schema {schema_name} written to {output_path}")
            except Exception as e:
                print(f"Error writing {schema_name}: {e}")

    return 0 if found_count == 3 else 1

# Returns: {"registration-schema": {...}, "configuration-schema": {...}, "status-schema": {...}}
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Client Device Discovery: Collapse and Package schemas from the CDD repository",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--source", required=True, type=str, help="Path to <cdd repo>/src/schemas/")
    parser.add_argument("--destination", required=True, type=str, help="Path to <DiscoveryTestServicePOC>/src/compiled_schemas/")
    args = parser.parse_args()

    exit(main(args.source, args.destination))