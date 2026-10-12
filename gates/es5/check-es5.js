#!/usr/bin/env node
/*
 * WebSquare 화면(XML)과 .js 파일이 ES5 문법만 쓰는지 검사한다.
 *
 * 사용법: node check-es5.js <파일 또는 디렉터리>...
 * 종료 코드: 0 = 통과, 1 = 위반 있음, 2 = 사용법 오류
 *
 * 그 줄만 검사에서 빼려면 줄 끝에 `// es5-ignore` 주석을 단다 (API 검사에만 적용).
 */
'use strict';

const fs = require('fs');
const path = require('path');
const acorn = require('acorn');

// ES5 문법이지만 대상 런타임에 없는 API. 문법 검사로는 안 잡히므로 따로 본다.
const FORBIDDEN_APIS = [
  { re: /\bPromise\b/, name: 'Promise' },
  { re: /\bfetch\s*\(/, name: 'fetch()' },
  { re: /\.includes\s*\(/, name: 'Array/String.prototype.includes' },
  { re: /\bObject\.assign\b/, name: 'Object.assign' },
  { re: /\bObject\.entries\b/, name: 'Object.entries' },
  { re: /\bObject\.values\b/, name: 'Object.values' },
  { re: /\bArray\.from\b/, name: 'Array.from' },
  { re: /\.find(Index)?\s*\(/, name: 'Array.prototype.find/findIndex' },
  { re: /\.startsWith\s*\(|\.endsWith\s*\(/, name: 'String.prototype.startsWith/endsWith' },
  { re: /\bnew\s+(Map|Set|WeakMap|WeakSet)\b/, name: 'Map/Set' },
  { re: /\bSymbol\s*\(/, name: 'Symbol' },
];

// WebSquare XML의 <script ...> ... </script> 블록. CDATA 감싸기는 있어도 없어도 된다.
const SCRIPT_RE = /<script\b[^>]*>([\s\S]*?)<\/script>/gi;
const CDATA_RE = /^(\s*<!\[CDATA\[)([\s\S]*?)\]\]>\s*$/;

function collectFiles(target, out) {
  const stat = fs.statSync(target);
  if (stat.isDirectory()) {
    for (const name of fs.readdirSync(target)) {
      if (name === 'node_modules' || name.startsWith('.')) continue;
      collectFiles(path.join(target, name), out);
    }
  } else if (/\.(xml|js)$/i.test(target)) {
    out.push(target);
  }
  return out;
}

function lineOf(text, index) {
  let line = 1;
  for (let i = 0; i < index; i++) if (text.charCodeAt(i) === 10) line++;
  return line;
}

// 파일에서 검사할 JS 조각을 뽑는다. 각 조각은 원본 파일 기준 시작 줄을 가진다.
function extractChunks(file, text) {
  if (/\.js$/i.test(file)) return [{ code: text, startLine: 1 }];

  const chunks = [];
  let m;
  SCRIPT_RE.lastIndex = 0;
  while ((m = SCRIPT_RE.exec(text)) !== null) {
    let body = m[1];
    let bodyIndex = m.index + m[0].indexOf('>') + 1;
    const cdata = CDATA_RE.exec(body);
    if (cdata) {
      bodyIndex += cdata[1].length;
      body = cdata[2];
    }
    if (body.trim()) chunks.push({ code: body, startLine: lineOf(text, bodyIndex) });
  }
  return chunks;
}

function checkChunk(file, chunk, sourceLines) {
  const problems = [];

  try {
    acorn.parse(chunk.code, { ecmaVersion: 5, sourceType: 'script', locations: true });
  } catch (e) {
    const line = e.loc ? chunk.startLine + e.loc.line - 1 : chunk.startLine;
    problems.push({ line, kind: 'ES5 문법', msg: e.message.replace(/\s*\(\d+:\d+\)$/, '') });
  }

  chunk.code.split('\n').forEach((text, i) => {
    if (/es5-ignore/.test(text)) return;
    const stripped = text.replace(/\/\/.*$/, '');
    for (const api of FORBIDDEN_APIS) {
      if (api.re.test(stripped)) {
        problems.push({ line: chunk.startLine + i, kind: '미지원 API', msg: api.name });
      }
    }
  });

  return problems.map((p) => ({ ...p, file, source: (sourceLines[p.line - 1] || '').trim() }));
}

function main(argv) {
  if (argv.length === 0) {
    console.error('사용법: node check-es5.js <파일 또는 디렉터리>...');
    return 2;
  }

  const files = [];
  for (const t of argv) collectFiles(t, files);

  let total = 0;
  for (const file of files) {
    const text = fs.readFileSync(file, 'utf8');
    const sourceLines = text.split('\n');
    for (const chunk of extractChunks(file, text)) {
      for (const p of checkChunk(file, chunk, sourceLines)) {
        total++;
        console.log(`${p.file}:${p.line}  [${p.kind}] ${p.msg}`);
        if (p.source) console.log(`    ${p.source}`);
      }
    }
  }

  console.log(`\n검사 파일 ${files.length}개, 위반 ${total}건`);
  return total > 0 ? 1 : 0;
}

process.exitCode = main(process.argv.slice(2));
