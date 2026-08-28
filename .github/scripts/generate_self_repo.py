"""Build a self-hosted Mihon extension repo (index.json/index.pb) from locally
built extension modules, for personal forks that don't run the full
keiyoushi/extensions publishing pipeline.

Usage: python generate_self_repo.py <output-dir>

Scans src/*/*/build/keiyoushi-source-info.json for already-built modules,
copies their apk/jar next to the index, and points resource URLs at
raw.githubusercontent.com on the `repo` branch of $GITHUB_REPOSITORY.
"""

import gzip
import json
import os
import shutil
import sys
from pathlib import Path

import index_pb2
from google.protobuf import json_format

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(sys.argv[1])
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]

RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/repo"
ICON_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/main"
ICON_FILE = "res/mipmap-xhdpi/ic_launcher.png"


def get_icon_url(module: str, theme: str | None) -> str:
    module_icon = f"src/{module.replace('.', '/')}/{ICON_FILE}"
    if (REPO_ROOT / module_icon).exists():
        return f"{ICON_BASE_URL}/{module_icon}"

    if theme:
        theme_icon = f"lib-multisrc/{theme}/{ICON_FILE}"
        if (REPO_ROOT / theme_icon).exists():
            return f"{ICON_BASE_URL}/{theme_icon}"

    return f"{ICON_BASE_URL}/core/src/main/{ICON_FILE}"


apk_dir = OUTPUT_DIR / "apk"
apk_dir.mkdir(parents=True, exist_ok=True)

extensions: list[index_pb2.Extension] = []

for info_file in sorted(REPO_ROOT.glob("src/*/*/build/keiyoushi-source-info.json")):
    with info_file.open(encoding="utf-8") as f:
        info = json.load(f)

    build_dir = info_file.parent
    apk = next((build_dir / "outputs/apk/release").glob("*.apk"), None)
    jar = next((build_dir / "outputs/jar/release").glob("*.jar"), None)
    if apk is None or jar is None:
        raise FileNotFoundError(
            f"{info['packageName']}: no release apk/jar found under {build_dir}"
        )

    shutil.copy2(apk, apk_dir / apk.name)
    shutil.copy2(jar, apk_dir / jar.name)

    extensions.append(
        index_pb2.Extension(
            name=info["name"],
            packageName=info["packageName"],
            resources=index_pb2.Resources(
                apkUrl=f"{RAW_BASE}/apk/{apk.name}",
                jarUrl=f"{RAW_BASE}/apk/{jar.name}",
                iconUrl=get_icon_url(info["module"], info.get("theme")),
            ),
            extensionLib=info["extensionLib"],
            versionCode=info["versionCode"],
            versionName=info["versionName"],
            contentWarning=info["contentWarning"],
            sources=[
                index_pb2.Source(
                    id=int(source["id"]),
                    name=source["name"],
                    language=source["lang"],
                    homeUrl=source["baseUrl"],
                    mirrorUrls=source.get("mirrorUrls", []),
                )
                for source in info["sources"]
            ],
        )
    )

if not extensions:
    raise RuntimeError("No built extensions found (no keiyoushi-source-info.json)")

extensions.sort(key=lambda ext: ext.packageName)

index = index_pb2.Index(
    name="My Mihon Extensions",
    badgeLabel="SELF",
    extensionList=index_pb2.ExtensionList(extensions=extensions),
)

with (OUTPUT_DIR / "index.json").open("w", encoding="utf-8") as f:
    f.write(
        json_format.MessageToJson(
            index,
            always_print_fields_with_no_presence=False,
            preserving_proto_field_name=True,
        )
    )

with (OUTPUT_DIR / "index.pb").open("wb") as f:
    f.write(gzip.compress(index.SerializeToString(deterministic=True), mtime=0))

print(f"Generated repo index with {len(extensions)} extension(s).")
