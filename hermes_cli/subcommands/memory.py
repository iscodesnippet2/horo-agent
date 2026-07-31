"""Built-in local memory CLI parser for the lite build."""

from __future__ import annotations


def build_memory_parser(subparsers, cmd_memory=None):
    parser = subparsers.add_parser(
        "memory",
        help="Manage built-in local memory",
        description=(
            "Manage Horo Agent's built-in local memory files. External memory "
            "providers are disabled in the lite build."
        ),
    )
    memory_sub = parser.add_subparsers(dest="memory_command")

    memory_sub.add_parser(
        "off",
        help="Disable external memory providers and use built-in local memory only",
    )

    reset = memory_sub.add_parser(
        "reset",
        help="Delete built-in local memory files",
    )
    reset.add_argument(
        "target",
        nargs="?",
        choices=("all", "memory", "user"),
        default="all",
        help="Which memory file to reset",
    )
    reset.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Do not prompt before deleting memory files",
    )

    for name in ("pending", "approve", "reject", "approval"):
        sub = memory_sub.add_parser(name, help=f"Memory write approval: {name}")
        sub.add_argument("args", nargs="*")

    if cmd_memory is not None:
        parser.set_defaults(func=cmd_memory)
    return parser
