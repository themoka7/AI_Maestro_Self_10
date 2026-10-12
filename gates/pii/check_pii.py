#!/usr/bin/env python3
"""SP(SQL) 파일이 승인 없이 개인정보 컬럼에 접근하는지 검사한다.

사용법:
    python3 check_pii.py --columns pii_columns.txt <파일 또는 디렉터리>...

규칙:
    1. 민감 컬럼 목록에 있는 컬럼을 참조하면, 같은 파일에
       `-- PII-APPROVED: <근거> : <컬럼>, <컬럼>` 주석이 있어야 한다.
    2. `SELECT *` 는 승인 여부와 관계없이 실패한다 (민감 컬럼 노출과 검사 우회 가능).

종료 코드: 0 = 통과, 1 = 위반 있음, 2 = 사용법 오류
"""

import argparse
import re
import sys
from pathlib import Path

SQL_SUFFIXES = {".sql", ".prc", ".pls", ".pkb"}
APPROVAL_RE = re.compile(r"--\s*PII-APPROVED\s*:(?P<body>.*)$", re.IGNORECASE | re.MULTILINE)
SELECT_STAR_RE = re.compile(r"\bSELECT\s+(?:DISTINCT\s+)?(?:\w+\.)?\*", re.IGNORECASE)
LINE_COMMENT_RE = re.compile(r"--.*$")
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
STRING_RE = re.compile(r"'(?:[^']|'')*'")


def load_columns(path):
    cols = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            cols.add(line.upper())
    return cols


def collect_files(targets):
    for t in targets:
        p = Path(t)
        if p.is_dir():
            yield from sorted(f for f in p.rglob("*") if f.suffix.lower() in SQL_SUFFIXES)
        elif p.suffix.lower() in SQL_SUFFIXES:
            yield p


def approved_columns(text):
    approved = set()
    for m in APPROVAL_RE.finditer(text):
        # "근거 : COL1, COL2" 형식. 마지막 ':' 뒤를 컬럼 목록으로 본다.
        body = m.group("body")
        cols = body.rsplit(":", 1)[-1] if ":" in body else ""
        approved.update(c.strip().upper() for c in cols.split(",") if c.strip())
    return approved


def code_only(text):
    """주석과 문자열 리터럴을 공백으로 바꾼다. 줄 번호를 유지하려고 줄바꿈은 남긴다."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    text = BLOCK_COMMENT_RE.sub(blank, text)
    text = STRING_RE.sub(blank, text)
    return "\n".join(LINE_COMMENT_RE.sub("", line) for line in text.split("\n"))


def check_file(path, pii_columns):
    text = path.read_text(encoding="utf-8")
    approved = approved_columns(text)
    code = code_only(text)
    src_lines = text.split("\n")
    problems = []

    for lineno, line in enumerate(code.split("\n"), start=1):
        if SELECT_STAR_RE.search(line):
            problems.append((lineno, "SELECT *", "컬럼을 명시해야 함", src_lines[lineno - 1]))
        for token in sorted(set(re.findall(r"[A-Za-z_][A-Za-z0-9_$#]*", line))):
            col = token.upper()
            if col in pii_columns and col not in approved:
                problems.append((lineno, "개인정보 컬럼", col, src_lines[lineno - 1]))

    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--columns", required=True, help="민감 컬럼 목록 파일 (한 줄에 하나)")
    ap.add_argument("targets", nargs="+", help="검사할 파일 또는 디렉터리")
    args = ap.parse_args(argv)

    pii_columns = load_columns(args.columns)
    files = list(collect_files(args.targets))
    total = 0
    for f in files:
        for lineno, kind, msg, src in check_file(f, pii_columns):
            total += 1
            print(f"{f}:{lineno}  [{kind}] {msg}")
            print(f"    {src.strip()}")

    print(f"\n검사 파일 {len(files)}개, 위반 {total}건")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
