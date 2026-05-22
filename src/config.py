from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root:           Path   # ProjetoIntegrador-I/
    data:           Path   # data/
    data_raw:       Path   # data/raw/
    data_clean:     Path   # data/clean/
    data_processed: Path   # data/processed/
    data_mapping:   Path   # data/mapping/
    reports:        Path   # reports/
    reports_ml:     Path   # reports/ml/
    src:            Path   # src/
    core:           Path   # src/core/
    ui:             Path   # src/ui/
    config:         Path   # src/config/
    pipeline:       Path   # src/core/pipeline/
    notebooks:      Path   # notebooks/
    docs:           Path   # docs/


def get_project_paths(root: Path | None = None) -> ProjectPaths:
    project_root = root or Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    src_dir  = project_root / "src"

    return ProjectPaths(
        root           = project_root,
        data           = data_dir,
        data_raw       = data_dir / "raw",
        data_clean     = data_dir / "clean",
        data_processed = data_dir / "processed",
        data_mapping   = data_dir / "mapping",
        reports        = project_root / "reports",
        reports_ml     = project_root / "reports" / "ml",
        src            = src_dir,
        core           = src_dir / "core",
        ui             = src_dir / "ui",
        config         = src_dir / "config",
        pipeline       = src_dir / "pipeline",
        notebooks      = project_root / "notebooks",
        docs           = project_root / "docs",
    )

# Instância global, só importar em qualquer módulo do projeto
PATHS = get_project_paths()
