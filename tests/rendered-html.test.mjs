import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

test("public 静态资产与根目录源文件同步", () => {
  const result = spawnSync(
    process.execPath,
    [resolve(projectRoot, "tooling", "sync-static-assets.mjs"), "--check"],
    { cwd: projectRoot, encoding: "utf8" },
  );

  assert.equal(result.status, 0, [result.stdout, result.stderr].filter(Boolean).join("\n"));
});

test("刷题 HTML 使用有效的本地静态引用", async () => {
  const htmlPath = resolve(projectRoot, "index.html");
  const html = await readFile(htmlPath, "utf8");

  assert.match(html, /<html\s+lang="zh-CN">/i);
  assert.match(html, /<meta\s+charset="UTF-8">/i);
  assert.ok(
    html.includes(`banks/' + bank + '.js`),
    "题库脚本必须使用相对于刷题页的 banks/ 路径",
  );

  const defaultBank = html.match(/p\.get\(['"]bank['"]\)\s*\|\|\s*['"]([^'"]+)['"]/);
  assert.ok(defaultBank, "没有找到默认题库配置");
  await access(resolve(projectRoot, "banks", `${defaultBank[1]}.js`));

  for (const globalName of ["QUIZ_META", "questionData", "QUESTION_CHAPS", "CAT_MAP", "SONG_LINES"]) {
    assert.ok(html.includes(globalName), `刷题页没有引用 ${globalName}`);
  }

  const staticReferences = [...html.matchAll(/\b(?:href|src)="([^"#]+)"/gi)]
    .map((match) => match[1])
    .filter(
      (reference) =>
        !/^(?:[a-z]+:|\/\/)/i.test(reference) && !/[+'{}]/.test(reference),
    );
  for (const reference of staticReferences) {
    const path = reference.split(/[?#]/, 1)[0];
    await access(resolve(dirname(htmlPath), path));
  }
});
