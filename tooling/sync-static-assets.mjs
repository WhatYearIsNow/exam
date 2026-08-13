#!/usr/bin/env node

import {
  mkdir,
  readFile,
  readdir,
  unlink,
  writeFile,
} from "node:fs/promises";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { TextDecoder } from "node:util";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceBanksDirectory = resolve(projectRoot, "banks");
const publishedBanksDirectory = resolve(projectRoot, "public", "banks");
const utf8Decoder = new TextDecoder("utf-8", { fatal: true });

function displayPath(path) {
  return relative(projectRoot, path).replaceAll("\\", "/");
}

async function readUtf8(path) {
  const content = await readFile(path);

  try {
    utf8Decoder.decode(content);
  } catch {
    throw new Error(`${displayPath(path)} 不是有效的 UTF-8 文件`);
  }

  return content;
}

async function listJavaScriptFiles(directory) {
  try {
    return (await readdir(directory, { withFileTypes: true }))
      .filter((entry) => entry.isFile() && entry.name.endsWith(".js"))
      .map((entry) => entry.name)
      .sort();
  } catch (error) {
    if (error.code === "ENOENT") {
      return [];
    }
    throw error;
  }
}

async function getAssetPairs() {
  const bankNames = await listJavaScriptFiles(sourceBanksDirectory);
  const pairs = [
    [resolve(projectRoot, "index.html"), resolve(projectRoot, "public", "quiz.html")],
    [resolve(projectRoot, "LICENSE"), resolve(projectRoot, "public", "LICENSE.txt")],
    ...bankNames.map((name) => [
      resolve(sourceBanksDirectory, name),
      resolve(publishedBanksDirectory, name),
    ]),
  ];

  return { bankNames, pairs };
}

async function checkAssets() {
  const { bankNames, pairs } = await getAssetPairs();
  const problems = [];

  for (const [source, destination] of pairs) {
    const sourceContent = await readUtf8(source);

    try {
      const destinationContent = await readUtf8(destination);
      if (!sourceContent.equals(destinationContent)) {
        problems.push(`${displayPath(destination)} 与 ${displayPath(source)} 不一致`);
      }
    } catch (error) {
      if (error.code === "ENOENT") {
        problems.push(`缺少 ${displayPath(destination)}`);
      } else {
        throw error;
      }
    }
  }

  const sourceBankNames = new Set(bankNames);
  const extraBankNames = (await listJavaScriptFiles(publishedBanksDirectory)).filter(
    (name) => !sourceBankNames.has(name),
  );
  for (const name of extraBankNames) {
    problems.push(`public/banks/${name} 没有对应的源题库`);
  }

  if (problems.length > 0) {
    for (const problem of problems) {
      console.error(`- ${problem}`);
    }
    process.exitCode = 1;
    return;
  }

  console.log(`静态资产已同步（${pairs.length} 个文件）`);
}

async function syncAssets() {
  const { bankNames, pairs } = await getAssetPairs();

  for (const [source, destination] of pairs) {
    const content = await readUtf8(source);
    await mkdir(dirname(destination), { recursive: true });
    await writeFile(destination, content);
  }

  const sourceBankNames = new Set(bankNames);
  const extraBankNames = (await listJavaScriptFiles(publishedBanksDirectory)).filter(
    (name) => !sourceBankNames.has(name),
  );
  for (const name of extraBankNames) {
    await unlink(resolve(publishedBanksDirectory, name));
  }

  console.log(`已同步 ${pairs.length} 个静态资产`);
}

const argumentsList = process.argv.slice(2);
if (argumentsList.length > 1 || (argumentsList.length === 1 && argumentsList[0] !== "--check")) {
  console.error("用法：node tooling/sync-static-assets.mjs [--check]");
  process.exitCode = 2;
} else if (argumentsList[0] === "--check") {
  await checkAssets();
} else {
  await syncAssets();
}
