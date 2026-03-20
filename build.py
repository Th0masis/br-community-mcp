import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_artifacts():
    for d in ["build", "dist"]:
        p = Path(d)
        if p.exists():
            print(f"Removing {p}/")
            shutil.rmtree(p)


def build():
    spec_file = Path("br_community_mcp.spec")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(spec_file), "--noconfirm"],
        check=False,
    )
    if result.returncode != 0:
        sys.exit(result.returncode)
    output = (
        Path("dist/br-community-mcp.exe")
        if sys.platform == "win32"
        else Path("dist/br-community-mcp")
    )
    if output.exists():
        print(
            f"Build successful: {output} ({output.stat().st_size / (1024*1024):.1f} MB)"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    if args.clean:
        clean_build_artifacts()
    build()


if __name__ == "__main__":
    main()
