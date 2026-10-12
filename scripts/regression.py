#!/usr/bin/env python3
"""품질 게이트 회귀 시험.

samples/regression/ 의 사례 파일마다 맞는 게이트(ES5 또는 개인정보)를 돌리고,
파일 상단 주석의 "기대 줄"에서 "기대 탐지" 유형으로 잡히면 적발로 센다.

사용법: python3 scripts/regression.py [사례 디렉터리]
종료 코드: 0 = 전부 적발, 1 = 놓친 사례 있음
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ES5_GATE = ["node", str(ROOT / "gates/es5/check-es5.js")]
PII_GATE = ["python3", str(ROOT / "gates/pii/check_pii.py"), "--columns", str(ROOT / "gates/pii/pii_columns.txt")]

TYPE_RE = re.compile(r"재현 유형:\s*(.+)")
EXPECT_RE = re.compile(r"기대 탐지:\s*(.+)")
LINE_RE = re.compile(r"기대 줄:\s*(\d+)")


def read_header(path):
    head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
    kind, expect, line = TYPE_RE.search(head), EXPECT_RE.search(head), LINE_RE.search(head)
    if not (kind and expect and line):
        sys.exit(f"{path}: 상단 주석에 '재현 유형', '기대 탐지', '기대 줄'이 필요함")
    return kind.group(1).strip(), expect.group(1).strip(), int(line.group(1))


def run_gate(path):
    if path.suffix.lower() == ".xml" or path.suffix.lower() == ".js":
        gate, cmd = "ES5", ES5_GATE
    else:
        gate, cmd = "개인정보", PII_GATE
    proc = subprocess.run(cmd + [str(path)], capture_output=True, text=True)
    return gate, proc.returncode, proc.stdout


def main():
    case_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "samples/regression"
    cases = sorted(p for p in case_dir.iterdir() if p.suffix.lower() in {".xml", ".js", ".sql"})

    rows, totals = [], {}
    for path in cases:
        kind, expect, line = read_header(path)
        gate, code, out = run_gate(path)
        # 기대한 줄에서 기대한 유형으로 잡혀야 적발로 센다 (다른 이유의 오류는 적발이 아님)
        caught = code == 1 and any(
            f"{path.name}:{line} " in o and expect in o for o in out.splitlines()
        )
        rows.append((gate, path.name, kind, expect, line, caught))
        hit, n = totals.get(gate, (0, 0))
        totals[gate] = (hit + caught, n + 1)

    print("| 게이트 | 사례 파일 | 재현 유형 | 기대 탐지 | 결과 |")
    print("|--------|----------|----------|----------|------|")
    for gate, name, kind, expect, line, caught in rows:
        print(f"| {gate} | `{name}` | {kind} | {line}행 `{expect}` | {'적발' if caught else '**놓침**'} |")

    print()
    print("| 게이트 | 적발 |")
    print("|--------|------|")
    all_hit = all_n = 0
    for gate, (hit, n) in totals.items():
        print(f"| {gate} | {hit}/{n}건 |")
        all_hit, all_n = all_hit + hit, all_n + n
    print(f"| **합계** | **{all_hit}/{all_n}건** |")

    return 0 if all_hit == all_n else 1


if __name__ == "__main__":
    sys.exit(main())
