# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hidden_imports = [
    # MCP SDK internals
    "mcp",
    "mcp.server",
    "mcp.server.fastmcp",
    "mcp.server.stdio",
    "mcp.server.sse",
    "mcp.server.streamable_http",
    "mcp.types",
    "mcp.shared",
    "mcp.shared.exceptions",
    # ASGI / HTTP stack (used by MCP even in stdio mode)
    "starlette",
    "starlette.applications",
    "starlette.routing",
    "starlette.requests",
    "starlette.responses",
    "starlette.middleware",
    "anyio",
    "anyio._backends",
    "anyio._backends._asyncio",
    "httpx",
    "httpcore",
    "sniffio",
    "h11",
    "certifi",
    "idna",
    # Pydantic
    "pydantic",
    "pydantic.fields",
    "pydantic._internal",
    "pydantic_core",
    "annotated_types",
    "typing_extensions",
    # Standard library
    "json",
    "hashlib",
    "logging",
    "re",
    # Source package
    "src",
    "src.server",
    "src.models",
    "src.utils",
    # Async
    "asyncio",
    "concurrent.futures",
]

a = Analysis(
    ["src/server.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas", "PIL"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="br-community-mcp",
    debug=False,
    strip=False,
    upx=True,
    console=True,
    runtime_tmpdir=None,
)
