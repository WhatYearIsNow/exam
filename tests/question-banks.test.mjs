import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const banksDirectory = resolve(projectRoot, "banks");
const bankNames = (await readdir(banksDirectory))
  .filter((name) => name.endsWith(".js") && !name.startsWith("_"))
  .sort();

function loadBank(source, filename) {
  const context = {};
  vm.runInNewContext(
    `${source}\n;globalThis.__bank = { QUIZ_META, questionData, QUESTION_CHAPS, CAT_MAP, SONG_LINES };`,
    context,
    { filename, timeout: 1_000 },
  );
  return context.__bank;
}

test("仓库至少包含一个正式题库", () => {
  assert.ok(bankNames.length > 0);
});

for (const bankName of bankNames) {
  test(`${bankName} 可加载且结构合法`, async () => {
    const source = await readFile(resolve(banksDirectory, bankName), "utf8");
    const { QUIZ_META, questionData, QUESTION_CHAPS, CAT_MAP, SONG_LINES } = loadBank(
      source,
      bankName,
    );

    assert.equal(typeof QUIZ_META, "object");
    assert.ok(QUIZ_META.subject.trim());
    assert.ok(QUIZ_META.version.trim());
    assert.ok(Number.isInteger(QUIZ_META.totalQuestions));
    assert.equal(QUIZ_META.totalQuestions, questionData.length);
    assert.equal(QUESTION_CHAPS.length, questionData.length);
    assert.ok(Object.keys(CAT_MAP).length > 0);
    assert.ok(SONG_LINES.length > 0);
    assert.ok(SONG_LINES.every((line) => typeof line === "string" && line.trim()));

    const titles = new Set();
    for (const [index, question] of questionData.entries()) {
      const label = `${bankName} 第 ${index + 1} 题`;
      assert.ok(question.title.trim(), `${label} 缺少 title`);
      assert.match(question.title, /\d+/, `${label} 的 title 缺少题号`);
      assert.ok(!titles.has(question.title), `${label} 的 title 重复`);
      titles.add(question.title);

      assert.ok(question.desc.trim(), `${label} 缺少 desc`);
      assert.equal(typeof question.code, "string", `${label} 的 code 必须是字符串`);
      assert.ok(question.analysis.trim(), `${label} 缺少 analysis`);
      assert.equal(question.options.length, 4, `${label} 必须有四个选项`);

      const optionLabels = question.options.map((option) => {
        assert.ok(typeof option === "string" && option.trim(), `${label} 存在空选项`);
        const match = option.match(/^([A-Z])\.\s*/);
        assert.ok(match, `${label} 的选项缺少字母前缀`);
        return match[1];
      });
      assert.equal(new Set(optionLabels).size, optionLabels.length, `${label} 的选项字母重复`);

      assert.match(question.answer, /^[A-Z]+$/, `${label} 的 answer 格式错误`);
      assert.equal(
        new Set(question.answer).size,
        question.answer.length,
        `${label} 的 answer 包含重复字母`,
      );
      for (const answer of question.answer) {
        assert.ok(optionLabels.includes(answer), `${label} 的答案 ${answer} 没有对应选项`);
      }

      const chapter = QUESTION_CHAPS[index];
      assert.ok(typeof chapter === "string" && chapter.trim(), `${label} 缺少章节`);
      assert.ok(Object.hasOwn(CAT_MAP, chapter), `${label} 的章节未在 CAT_MAP 中定义`);
    }
  });
}
