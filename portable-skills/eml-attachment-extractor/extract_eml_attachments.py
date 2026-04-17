"""
从 .eml 邮件文件中批量提取附件（带内容哈希去重）。

用法:
    python extract_eml_attachments.py <源目录> <目标目录> [选项]

参数:
    source_dir   包含 .eml 文件的源目录
    target_dir   附件保存的目标目录

选项:
    --overwrite       覆盖已存在的文件
    --ext FILTER      只提取指定扩展名的附件（如 --ext .pdf .docx）
    --log LOG_FILE    将日志写入指定文件（默认输出到控制台）
    --dry-run         仅预览，不实际提取

去重策略（三级）:
    1. 文件名相同 + SHA256 相同 → 跳过（完全重复）
    2. 文件名相同 + SHA256 不同 → 重命名保存（同名不同内容）
    3. 文件名不同 + SHA256 相同 → 跳过并提示（不同名但内容重复）
"""

import argparse
import email
import hashlib
import os
import glob
import sys
from email import policy


def decode_filename(part):
    """从 MIME part 中解码附件文件名。"""
    filename = part.get_filename()
    if filename:
        return filename
    raw = part.get("Content-Disposition")
    if raw:
        for item in raw.split(";"):
            item = item.strip()
            if item.lower().startswith("filename"):
                _, _, val = item.partition("=")
                return val.strip().strip('"')
    return None


def sha256(data):
    """计算字节数据的 SHA256 哈希值。"""
    return hashlib.sha256(data).hexdigest()


def extract_attachments_from_eml(eml_path):
    """从单个 eml 文件中提取所有附件。返回 [(filename, payload_bytes), ...]"""
    with open(eml_path, "rb") as f:
        msg = email.message_from_bytes(f.read(), policy=policy.default)

    attachments = []
    for part in msg.walk():
        content_disposition = part.get("Content-Disposition", "")
        if "attachment" not in content_disposition:
            continue

        filename = decode_filename(part)
        if not filename:
            continue

        try:
            payload = part.get_content()
            attachments.append((filename, payload))
        except Exception as e:
            attachments.append((filename, e))

    return attachments


def build_target_index(target_dir):
    """扫描目标目录已有文件，建立 文件名→路径、哈希→文件名 的索引。"""
    existing = [f for f in os.listdir(target_dir)
                if os.path.isfile(os.path.join(target_dir, f))]
    name_index = {f.lower(): f for f in existing}
    hash_index = {}
    for f in existing:
        try:
            h = sha256(open(os.path.join(target_dir, f), "rb").read())
            hash_index[h] = f.lower()
        except Exception:
            pass
    return name_index, hash_index


def unique_filename(target_dir, filename, name_index):
    """生成不冲突的唯一文件名，格式: name(2).ext, name(3).ext ..."""
    name, ext = os.path.splitext(filename)
    counter = 2
    while True:
        new_name = f"{name}({counter}){ext}"
        if new_name.lower() not in name_index:
            return new_name
        counter += 1


def main():
    parser = argparse.ArgumentParser(
        description="从 .eml 邮件文件中批量提取附件（带内容哈希去重）"
    )
    parser.add_argument("source_dir", help="包含 .eml 文件的源目录")
    parser.add_argument("target_dir", help="附件保存的目标目录")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="覆盖已存在的文件（默认智能去重）",
    )
    parser.add_argument(
        "--ext",
        nargs="+",
        default=None,
        help="只提取指定扩展名的附件（如 --ext .pdf .docx）",
    )
    parser.add_argument(
        "--log",
        default=None,
        help="将日志写入指定文件",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="仅预览，不实际提取",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.source_dir):
        print(f"错误: 源目录不存在: {args.source_dir}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.target_dir, exist_ok=True)

    ext_filter = None
    if args.ext:
        ext_filter = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in args.ext}

    # 建立目标目录索引
    name_index, hash_index = build_target_index(args.target_dir)

    eml_files = sorted(glob.glob(os.path.join(args.source_dir, "*.eml")))

    logs = []
    stats = {
        "extracted": 0, "skipped_name": 0, "skipped_hash": 0,
        "renamed": 0, "filtered": 0, "errors": 0, "no_attachment": 0,
    }

    logs.append(f"源目录: {args.source_dir}")
    logs.append(f"目标目录: {args.target_dir}")
    logs.append(f"找到 {len(eml_files)} 个 .eml 文件")
    logs.append(f"目标目录已有 {len(name_index)} 个文件")
    if ext_filter:
        logs.append(f"扩展名过滤: {', '.join(ext_filter)}")
    if args.dry_run:
        logs.append("** 预览模式 - 不实际写入文件 **")
    logs.append("")

    for eml_path in eml_files:
        eml_name = os.path.basename(eml_path)
        attachments = extract_attachments_from_eml(eml_path)

        if not attachments:
            stats["no_attachment"] += 1
            logs.append(f"  [无附件] {eml_name}")
            continue

        for filename, payload in attachments:
            if isinstance(payload, Exception):
                stats["errors"] += 1
                logs.append(f"  [错误] {filename}: {payload}")
                continue

            # 扩展名过滤
            if ext_filter:
                _, ext = os.path.splitext(filename)
                if ext.lower() not in ext_filter:
                    stats["filtered"] += 1
                    logs.append(f"  [过滤] {filename}")
                    continue

            file_hash = sha256(payload)

            if args.overwrite:
                # 覆盖模式：直接写入
                dst_path = os.path.join(args.target_dir, filename)
                if not args.dry_run:
                    with open(dst_path, "wb") as out:
                        out.write(payload)
                stats["extracted"] += 1
                logs.append(f"  [覆盖] {filename}")
                continue

            # --- 智能去重模式 ---

            # 级别 3: 内容相同但文件名不同 → 跳过并提示
            if file_hash in hash_index:
                existing_name = hash_index[file_hash]
                if existing_name != filename.lower():
                    stats["skipped_hash"] += 1
                    logs.append(f"  [内容重复] {filename} (与 {existing_name} 内容相同)")
                    continue

            # 级别 1: 文件名相同 + 内容相同 → 跳过
            if filename.lower() in name_index:
                stats["skipped_name"] += 1
                logs.append(f"  [跳过] 已存在: {filename}")
                continue

            # 级别 2: 文件名相同 + 内容不同 → 重命名
            save_name = filename
            if filename.lower() in name_index:
                save_name = unique_filename(args.target_dir, filename, name_index)
                stats["renamed"] += 1
                logs.append(f"  [重命名] {filename} -> {save_name} (同名不同内容)")

            # 保存
            if not args.dry_run:
                dst_path = os.path.join(args.target_dir, save_name)
                with open(dst_path, "wb") as out:
                    out.write(payload)
                name_index[save_name.lower()] = save_name
                hash_index[file_hash] = save_name.lower()

            stats["extracted"] += 1
            prefix = "[预览]" if args.dry_run else "[提取]"
            action = f" -> {save_name}" if save_name != filename else ""
            logs.append(f"  {prefix} {filename}{action}")

    logs.append("")
    logs.append(
        f"完成! 提取: {stats['extracted']}, "
        f"跳过(同名): {stats['skipped_name']}, "
        f"跳过(内容重复): {stats['skipped_hash']}, "
        f"重命名(同名不同内容): {stats['renamed']}, "
        f"过滤: {stats['filtered']}, "
        f"错误: {stats['errors']}, "
        f"无附件: {stats['no_attachment']}"
    )

    output = "\n".join(logs)

    if args.log:
        with open(args.log, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"日志已写入: {args.log}")
    else:
        try:
            print(output)
        except UnicodeEncodeError:
            print(output.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))

    return stats


if __name__ == "__main__":
    main()
