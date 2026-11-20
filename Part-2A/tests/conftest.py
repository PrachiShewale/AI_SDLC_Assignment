import importlib.util
import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
PACKAGE_NAME = "part_2a_src"

if PACKAGE_NAME not in sys.modules:
    package_spec = importlib.util.spec_from_file_location(
        PACKAGE_NAME,
        SOURCE_ROOT / "__init__.py",
        submodule_search_locations=[str(SOURCE_ROOT)],
    )
    if package_spec is None or package_spec.loader is None:
        raise ImportError(f"Unable to load Part-2A source package from {SOURCE_ROOT}")
    package = importlib.util.module_from_spec(package_spec)
    sys.modules[PACKAGE_NAME] = package
    package_spec.loader.exec_module(package)
