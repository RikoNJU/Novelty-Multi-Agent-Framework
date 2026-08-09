"""论文处理 CLI：把 PDF 处理为工作流兼容的 paper.json。"""

from __future__ import annotations

import argparse
from pathlib import Path

from ..config import build_model_registry, load_config
from ..persistence import persist_paper_input
from .paper_processor import DefaultPaperProcessor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="把论文 PDF 处理为工作流兼容的 paper.json")
    parser.add_argument("--input", type=Path, required=True, help="PDF 文件路径")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs"),
        help="Paper 工作目录根路径（默认 outputs/）",
    )
    parser.add_argument("--paper-id", default=None, help="覆盖 paper_id（默认取 PDF 文件名）")
    parser.add_argument("--force-ocr", action="store_true", help="强制走 DeepSeek-OCR 路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    config = load_config()
    registry = build_model_registry(config)
    processing_cfg = config.get("processing", {})
    ocr_client = registry.client_for(processing_cfg.get("ocr_model", "deepseek-ocr"))
    llm_client = registry.client_for(processing_cfg.get("llm_model", "r1-qwen3-8b"))

    processor = DefaultPaperProcessor(
        ocr_client=ocr_client,
        llm_client=llm_client,
        dpi=int(processing_cfg.get("dpi", 200)),
        min_chars_per_page=int(
            processing_cfg.get("quality_min_chars_per_page", 200)
        ),
    )
    document = processor.process(
        args.input,
        force_ocr=args.force_ocr,
        paper_id=args.paper_id,
    )
    compatible = processor.to_paper_input(document)

    workspace = persist_paper_input(document, compatible, output_root=args.output)
    print(f"Paper 工作目录：{workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
