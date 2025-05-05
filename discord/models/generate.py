import ast
import json
import logging
import pathlib
import tempfile
from fnmatch import fnmatch
from typing import Any

import black
import datamodel_code_generator as dcg
from typing_extensions import TypedDict


class GenerationError(Exception):
    pass


class SchemaType(TypedDict):
    openapi: str
    info: dict[str, Any]
    externalDocs: dict[str, Any]
    servers: list[dict[str, Any]]
    paths: dict[str, Any]
    components: dict[str, Any]


FLAGS_MAPPING = {"user": "UserFlags"}


def replace_flags(path: pathlib.Path):
    """
    Replace Int53Type flags annotations with proper class-specific flag types.

    Args:
        path: Path to the file to modify
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content)
    modified = False

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_name = node.name

            for class_item in node.body:
                if isinstance(class_item, ast.AnnAssign) and isinstance(
                    class_item.target, ast.Name
                ):
                    if (
                        class_item.target.id == "flags"
                        and isinstance(class_item.annotation, ast.Name)
                        and class_item.annotation.id == "Int53Type"
                    ):

                        flag_type = None
                        for pattern, flag_name in FLAGS_MAPPING.items():
                            if pattern.lower() in class_name.lower():
                                flag_type = flag_name
                                break

                        if flag_type:
                            class_item.annotation = ast.Name(
                                id=flag_type, ctx=ast.Load()
                            )
                            modified = True
                            logging.info(
                                f"Replaced flags annotation in {class_name} with {flag_type}"
                            )
                        else:
                            logging.warning(
                                f"Could not find appropriate flag type for {class_name}"
                            )

    if modified:
        with open(path, "w", encoding="utf-8") as f:
            f.write(ast.unparse(tree))
        logging.info(f"Updated flags annotations in {path}")
    else:
        logging.info(f"No flags annotations needed updating in {path}")


def get_classes_from_file(file_path: pathlib.Path):
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    return {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}


def are_classes_identical(class1: ast.ClassDef, class2: ast.ClassDef) -> bool:
    return (
        class1.name == class2.name
    )  # for now this is enough, as discord are smart enough not to reuse names


def remove_duplicates(source: pathlib.Path, dest: pathlib.Path):
    source_classes = get_classes_from_file(source)

    with open(dest, encoding="utf-8") as f:
        dest_content = f.read()

    dest_tree = ast.parse(dest_content)

    classes_to_remove: list[ast.ClassDef] = []
    for node in dest_tree.body:
        if isinstance(node, ast.ClassDef) and node.name in source_classes:
            classes_to_remove.append(node)

    for node in classes_to_remove:
        dest_tree.body.remove(node)

    logging.info(
        f"Removing {len(classes_to_remove)} identical classes from {dest.name}"
    )

    with open(dest, "w", encoding="utf-8") as f:
        f.write(ast.unparse(dest_tree))


def add_import(path: pathlib.Path, _import: str):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    first_class_index = next(
        (i for i, line in enumerate(lines) if line.strip().startswith("class ")), None
    )
    if first_class_index is not None:
        lines.insert(first_class_index, _import)

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)


def format(path: pathlib.Path) -> None:
    with open(path, encoding="utf-8") as f:
        content = f.read()

    new = black.format_str(
        content,
        mode=black.Mode(
            target_versions={
                black.TargetVersion.PY39,  # pyright: ignore [reportPrivateImportUsage]
                black.TargetVersion.PY310,  # pyright: ignore [reportPrivateImportUsage]
                black.TargetVersion.PY311,  # pyright: ignore [reportPrivateImportUsage]
            }
        ),
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)

    logging.info(f"Formatted {path.name}")


def apply_patches(path: pathlib.Path, patches: dict[str, str]):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    for old, new in patches.items():
        content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    logging.info(f"Applied patches to {path.name}")


def generate():
    openapi_path = pathlib.Path(__file__).parent / "openapi.json"
    routes_path = pathlib.Path(__file__).parent / "routes.txt"
    patches_path = pathlib.Path(__file__).parent / "patches.json"

    with open(openapi_path, encoding="utf-8") as f:
        openapi: SchemaType = json.loads(f.read())

    with open(patches_path, encoding="utf-8") as f:
        patches = json.loads(f.read())

    schemas_path = (
        pathlib.Path(__file__).parent / "generated" / "schemas" / "schemas.py"
    )

    with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
        temp_file.write(json.dumps(openapi).encode("utf-8"))

        temp_file_path = pathlib.Path(temp_file.name)
        dcg.generate(
            target_python_version=dcg.PythonVersion.PY_39,
            input_file_type=dcg.InputFileType.OpenAPI,
            input_=temp_file_path,
            output=schemas_path,
            use_standard_collections=True,
            use_union_operator=True,
            use_annotated=True,
            field_constraints=True,
            output_model_type=dcg.DataModelType.PydanticV2BaseModel,
            snake_case_field=True,
            use_schema_description=True,
            use_field_description=True,
            use_subclass_enum=True,
            openapi_scopes=[dcg.OpenAPIScope.Schemas],
            keep_model_order=True,
            strict_nullable=True,
        )
    logging.info("Schemas generated")

    replace_flags(schemas_path)
    add_import(schemas_path, "from ...flags import *\n\n")
    logging.info("Flags replaced")

    apply_patches(schemas_path, patches.get("schemas", {}))

    format(schemas_path)
    logging.info("Schemas formatted")

    with open(routes_path, encoding="utf-8") as f:
        routes = f.read().splitlines()

    for path in list(openapi["paths"].keys()):
        if not any(fnmatch(path, route) for route in routes):
            del openapi["paths"][path]

    paths: set[str] = {path.split("/")[1] for path in openapi["paths"].keys()}
    failures: set[str] = set()

    for path in paths:
        this_openapi = openapi.copy()
        this_openapi["paths"] = {
            k: v for k, v in this_openapi["paths"].items() if k.startswith(f"/{path}")
        }
        destination_path = (
            pathlib.Path(__file__).parent
            / "generated"
            / "paths"
            / f"{path.replace('-', '_')}.py"
        )
        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            temp_file.write(json.dumps(this_openapi).encode("utf-8"))
            temp_file_path = pathlib.Path(temp_file.name)
            try:
                dcg.generate(
                    target_python_version=dcg.PythonVersion.PY_39,
                    input_file_type=dcg.InputFileType.OpenAPI,
                    input_=temp_file_path,
                    output=destination_path,
                    use_standard_collections=True,
                    use_union_operator=True,
                    use_annotated=True,
                    field_constraints=True,
                    output_model_type=dcg.DataModelType.PydanticV2BaseModel,
                    snake_case_field=True,
                    use_schema_description=True,
                    use_field_description=True,
                    use_subclass_enum=True,
                    openapi_scopes=[dcg.OpenAPIScope.Paths],
                    keep_model_order=True,
                )
            except dcg.Error as e:
                if e.message == "Models not found in the input data":
                    logging.warning(f"Path {path} has no models, skipping")
                    failures.add(path)
                    continue
                raise GenerationError(f"Failed to generate {path}") from e
            except Exception as e:
                failures.add(path)
                raise GenerationError(f"Failed to generate {path}") from e
        logging.info(f"Path {path} generated")

        remove_duplicates(schemas_path, destination_path)
        logging.info(f"Duplicates removed from {path}")

        add_import(destination_path, "from ..schemas import *\n\n")

        format(destination_path)

        apply_patches(destination_path, patches.get(path, {}))

    paths -= failures

    init_file_path = (
        pathlib.Path(__file__).parent / "generated" / "paths" / "__init__.py"
    )
    with open(init_file_path, "w", encoding="utf-8") as f:
        for path in sorted(paths):
            f.write(f"from .{path.replace('-', '_')} import *\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate()
