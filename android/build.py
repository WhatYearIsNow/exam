#!/usr/bin/env python3
"""用 Android SDK 和 JDK 构建原生 WebView 壳，无需 Gradle。"""
import argparse
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parent


def exam_url(value):
    if any(c.isspace() or ord(c) < 32 for c in value) or "\\" in value:
        raise argparse.ArgumentTypeError("站点地址不能包含空白、控制字符或反斜杠")
    try:
        parsed = urllib.parse.urlsplit(value)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError
        if parsed.username is not None or parsed.password is not None:
            raise ValueError
        parsed.port  # Also reject malformed port numbers.
    except ValueError:
        raise argparse.ArgumentTypeError("EXAM_URL 必须是无凭证的完整 http(s) 地址")
    return value


def run(*command):
    subprocess.run([str(item) for item in command], check=True)


def build(args):
    sdk = args.sdk.expanduser().resolve()
    tools = sdk / "build-tools" / args.build_tools
    platform = sdk / "platforms" / ("android-" + str(args.platform)) / "android.jar"
    required = [platform] + [tools / name for name in ("aapt2", "d8", "zipalign")]
    for path in required:
        if not path.is_file():
            raise ValueError("缺少 Android SDK 组件：" + str(path))
    for command in ("javac", "jar", "java"):
        if not shutil.which(command):
            raise ValueError("未找到 " + command + "，请安装 JDK 并配置 PATH")

    output = args.out.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = ET.parse(ROOT / "AndroidManifest.xml").getroot()
    version = manifest.attrib["{http://schemas.android.com/apk/res/android}versionName"]
    destination = output / ("ILoveTJU-" + version + "-local-unsigned.apk")
    parsed = urllib.parse.urlsplit(args.url)

    # Keep the previous hand-built APKs and build/ contents intact.
    with tempfile.TemporaryDirectory(prefix="work-", dir=output) as temporary:
        work = Path(temporary)
        generated = work / "generated"
        generated.mkdir()
        assets = work / "assets"
        shutil.copytree(ROOT / "assets", assets)
        page = assets / "offline.html"
        url_json = json.dumps(args.url, ensure_ascii=True)
        script_url = url_json.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        page.write_text(page.read_text(encoding="utf-8").replace(
            "__EXAM_HOST_HTML__", html.escape(parsed.netloc)
        ).replace("__EXAM_URL_JSON__", script_url), encoding="utf-8")
        config = generated / "com" / "tju" / "quizhub" / "BuildConfig.java"
        config.parent.mkdir(parents=True)
        config.write_text(
            "package com.tju.quizhub;\n"
            "final class BuildConfig {\n"
            "    static final String EXAM_URL = " + url_json + ";\n"
            "    static final String EXAM_HOST = " + json.dumps(parsed.hostname) + ";\n"
            "}\n", encoding="utf-8")

        compiled = work / "res.zip"
        resources = work / "resources.apk"
        run(tools / "aapt2", "compile", "--dir", ROOT / "res", "-o", compiled)
        run(tools / "aapt2", "link", "-o", resources, "--manifest",
            ROOT / "AndroidManifest.xml", "-I", platform, "--java", generated,
            "-A", assets, compiled)
        classes = work / "classes"
        classes.mkdir()
        sources = sorted((ROOT / "java").rglob("*.java")) + sorted(generated.rglob("*.java"))
        run("javac", "--release", "8", "-encoding", "UTF-8", "-classpath",
            platform, "-d", classes, *sources)
        jar = work / "classes.jar"
        run("jar", "--create", "--file", jar, "-C", classes, ".")
        dex = work / "dex"
        dex.mkdir()
        run(tools / "d8", "--lib", platform, "--min-api", "24", "--output", dex, jar)
        unaligned = work / "unaligned.apk"
        shutil.copy2(resources, unaligned)
        with zipfile.ZipFile(unaligned, "a") as apk:
            for path in sorted(dex.glob("classes*.dex")):
                apk.write(path, path.name)
        aligned = work / "aligned.apk"
        run(tools / "zipalign", "-f", "-p", "4", unaligned, aligned)
        run(tools / "zipalign", "-c", "4", aligned)
        aligned.replace(destination)
    print("已构建（未签名）：", destination)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", type=exam_url, default=os.environ.get("EXAM_URL"),
                        help="部署站点完整地址；也可设置 EXAM_URL，必须显式提供")
    parser.add_argument("--sdk", type=Path, default=Path(
        os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
        or str(Path.home() / "Android" / "Sdk")), help="Android SDK 目录")
    parser.add_argument("--platform", type=int, default=34, help="SDK platform（默认 34）")
    parser.add_argument("--build-tools", default="34.0.0", help="SDK build-tools 版本（默认 34.0.0）")
    parser.add_argument("--out", type=Path, default=ROOT / "build" / "local",
                        help="输出目录，默认 android/build/local")
    args = parser.parse_args()
    if not args.url:
        parser.error("请通过 --url 或 EXAM_URL 显式指定部署站点")
    try:
        build(args)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, "构建失败：" + str(error) + "\n")


if __name__ == "__main__":
    main()
