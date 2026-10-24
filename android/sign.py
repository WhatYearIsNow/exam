#!/usr/bin/env python3
"""Sign an aligned APK and verify its identity before writing release output."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent


def password_source(value):
    if not value.startswith(('env:', 'file:')) or not value.split(':', 1)[1]:
        raise argparse.ArgumentTypeError('密码使用 env:变量名 或 file:本地文件，避免写入命令行')
    return value


def run(command):
    result = subprocess.run([str(item) for item in command], stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode:
        raise ValueError(result.stdout.strip()[:1600] or 'Android SDK command failed')
    return result.stdout


def certificate(apksigner, apk):
    output = run([apksigner, 'verify', '--verbose', '--print-certs', apk])
    digests = set(re.findall(r'Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]+)', output))
    if not digests:
        raise ValueError('无法读取 APK 的签名证书')
    return {value.lower() for value in digests}


def package_info(aapt, apk):
    output = run([aapt, 'dump', 'badging', apk])
    match = re.search(r"^package: name='([^']+)' versionCode='(\d+)'", output, re.M)
    if not match:
        raise ValueError('无法读取 APK 包名或版本号')
    return match.group(1), int(match.group(2))


def sign(args):
    tools = args.sdk.expanduser().resolve() / 'build-tools' / args.build_tools
    apksigner, aligner, aapt = (tools / name for name in ('apksigner', 'zipalign', 'aapt2'))
    for path in (apksigner, aligner, aapt, args.apk, args.keystore):
        if not path.is_file():
            raise ValueError('缺少文件：' + str(path))
    if args.out.resolve() in {args.apk.resolve(), args.keystore.resolve()}:
        raise ValueError('输出不能覆盖输入 APK 或签名库')
    if args.previous_apk and args.out.resolve() == args.previous_apk.resolve():
        raise ValueError('输出不能覆盖用于比对的历史 APK')
    previous_cert = certificate(apksigner, args.previous_apk) if args.previous_apk else None
    current_info = package_info(aapt, args.apk)
    if args.previous_apk:
        previous_info = package_info(aapt, args.previous_apk)
        if current_info[0] != previous_info[0]:
            raise ValueError('包名与历史 APK 不同，不能作为同一应用升级')
        if current_info[1] <= previous_info[1]:
            raise ValueError('versionCode 必须大于历史 APK')
    run([aligner, '-c', '4', args.apk])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='sign-', dir=args.out.parent) as temporary:
        signed = Path(temporary) / 'signed.apk'
        command = [apksigner, 'sign', '--ks', args.keystore, '--ks-pass', args.ks_pass,
                   '--out', signed]
        if args.alias:
            command += ['--ks-key-alias', args.alias]
        if args.key_pass:
            command += ['--key-pass', args.key_pass]
        run(command + [args.apk])
        current_cert = certificate(apksigner, signed)
        if previous_cert is not None and current_cert != previous_cert:
            raise ValueError('签名证书与历史 APK 不一致，未写入发布文件')
        run([aligner, '-c', '4', signed])
        signed.replace(args.out)
    print('已签名并验证：', args.out)
    print('包名 / versionCode：', current_info[0], current_info[1])
    print('证书 SHA-256：', ', '.join(sorted(current_cert)))
    print('APK SHA-256：', hashlib.sha256(args.out.read_bytes()).hexdigest())
    return args.out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('apk', type=Path, help='build.py 生成的 aligned unsigned APK')
    parser.add_argument('--out', required=True, type=Path, help='签名 APK 输出路径')
    parser.add_argument('--keystore', required=True, type=Path, help='现有签名库，不生成或替换密钥')
    parser.add_argument('--ks-pass', type=password_source, default='env:EXAM_ANDROID_STORE_PASSWORD')
    parser.add_argument('--key-pass', type=password_source, help='私钥密码与签名库密码不同时指定')
    parser.add_argument('--alias', help='签名库内的 key alias')
    parser.add_argument('--previous-apk', type=Path, help='检查同包名、同证书且 versionCode 递增')
    parser.add_argument('--sdk', type=Path, default=Path(os.environ.get('ANDROID_HOME')
                        or os.environ.get('ANDROID_SDK_ROOT') or str(Path.home() / 'Android/Sdk')))
    parser.add_argument('--build-tools', default='34.0.0')
    args = parser.parse_args()
    try:
        sign(args)
    except (OSError, ValueError) as error:
        parser.exit(1, '签名失败：' + str(error) + '\n')


if __name__ == '__main__':
    main()
