#!/usr/bin/env node
/**
 * 物理题库构建脚本（新格式 v2）
 *
 * 源格式：physics-quiz/source/*.md，一年一卷一文件，每题一个块：
 *   【题目来源】25261 大学物理1B T10
 *   【教材溯源】第10章 波动 - 10.6 波的干涉
 *   <题目正文：公式 $...$/$$...$$、图片 ![](images/xxx.jpg)、选项 A. B. C. D.>
 *   【答案】...
 *   【AI解析】...
 *
 * 输出：physics-quiz/physics-data.json（扁平题目列表）
 *       physics-quiz/images/（从 source/images/ 收集复制）
 *
 * 用法: node scripts/build-physics.mjs
 *       node scripts/build-physics.mjs --only 25261   # 只构建指定文件
 */

import { readFileSync, writeFileSync, mkdirSync, copyFileSync, existsSync, readdirSync } from 'fs';
import { join, basename } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const OUT_DIR = process.env.PHYSICS_OUT || join(ROOT, 'physics-quiz');
const SRC_DIR = process.env.PHYSICS_SRC || join(OUT_DIR, 'source');
const IMG_OUT = join(OUT_DIR, 'images');

const only = process.argv.includes('--only')
    ? process.argv[process.argv.indexOf('--only') + 1]
    : null;

// ─── 教材章节结构（《大学物理 下册》吴亚非，按教材顺序，含不涉及考题的小节）───
const TEXTBOOK_SECTIONS = {
    '第9章 振动': [
        '9.1 简谐振动', '9.2 阻尼振动', '9.3 受迫振动',
        '9.4 简谐振动的合成', '9.5 振动的分解、频谱'
    ],
    '第10章 波动': [
        '10.1 波动方程、平面简谐波', '10.2 波的能量、能流密度', '10.3 声波',
        '10.4 电磁波', '10.5 惠更斯原理', '10.6 波的干涉', '10.7 多普勒效应'
    ],
    '第11章 几何光学基础': [
        '11.1 几何光学的基本实验定律和基本原理', '11.2 单球面上的近轴成像', '11.3 薄透镜'
    ],
    '第12章 波动光学': [
        '12.1 光的干涉', '12.2 光的衍射', '12.3 光的偏振'
    ],
    '第13章 狭义相对论': [
        '13.1 总论', '13.2 洛伦兹变换与狭义相对论的时空观', '13.3 相对论力学'
    ],
    '第14章 物质的波粒二象性': [
        '14.1 黑体辐射与能量子', '14.2 光电效应与光子', '14.3 康普顿散射',
        '14.4 物质波与德布罗意关系', '14.5 氢原子和玻尔的量子论'
    ],
    '第15章 量子力学基础': [
        '15.1 物质波波函数的特性', '15.2 薛定谔方程', '15.3 一维定态系统',
        '15.4 氢原子', '15.5 电子的自旋 原子的壳层结构', '15.6 激光'
    ]
};

const NOTES_FILE = 'chapter-notes.md';

// 解析必备知识文件：【必备知识】第X章 章名 → markdown 正文
function parseNotes(text) {
    const notes = {};
    const blocks = text.split(/(?=^【必备知识】)/m).map(s => s.trim()).filter(Boolean);
    for (const block of blocks) {
        const label = block.match(/^【必备知识】\s*(.+?)\s*$/m)?.[1] || '';
        const body = block.slice(block.indexOf('\n')).trim();
        if (label && body) notes[label] = body;
    }
    return notes;
}

// ─── 解析单个文件 ───
function parseFile(text, fileId) {
    // 统一行尾，避免 CRLF 的 \r 干扰行级匹配
    text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    // 修复 LLM 转换事故：\nu 被还原成真换行（换行后紧跟 u 且非列表行）→ 换行补回为 \n，与后面的 u 组成 \nu
    text = text.replace(/\n(?=u(_|\b|[^\s.!#A-D【(（\[]))/g, '\\n');
    // 行内意外断行合并：换行后非列表/标签/空行时改为空格（保留图片行）
    text = text.replace(/([^\n])\n(?![\s\n]|\[|!|[A-D][.、．]|【|\(|（|\d+[.、．])/g, '$1 ');
    const questions = [];
    // 按【题目来源】切块（保留分隔符）
    const blocks = text.split(/(?=^【题目来源】)/m).map(s => s.trim()).filter(Boolean);

    for (const block of blocks) {
        if (!block.startsWith('【题目来源】')) continue;

        const source = block.match(/^【题目来源】\s*(.+?)\s*$/m)?.[1] || '';
        const chapterRaw = block.match(/^【教材溯源】\s*(.+?)\s*$/m)?.[1] || '第0章 未分类 - 0.0 待确认';

        const ansIdx = block.indexOf('【答案】');
        const anaIdx = block.indexOf('【AI解析】');

        // 正文：【题目正文】标签之后（无标签则教材溯源行之后）~ 【答案】之前
        let bodyStart;
        const bodyTagIdx = block.indexOf('【题目正文】');
        if (bodyTagIdx >= 0) {
            bodyStart = bodyTagIdx + '【题目正文】'.length;
        } else {
            const chapLineIdx = block.indexOf('【教材溯源】');
            bodyStart = chapLineIdx >= 0 ? block.indexOf('\n', chapLineIdx) + 1 : block.indexOf('\n') + 1;
        }
        const bodyEnd = ansIdx >= 0 ? ansIdx : block.length;
        let body = block.slice(bodyStart, bodyEnd).trim();

        const answer = ansIdx >= 0
            ? block.slice(ansIdx + '【答案】'.length, anaIdx >= 0 ? anaIdx : undefined).trim()
            : '';
        const analysis = anaIdx >= 0 ? block.slice(anaIdx + '【AI解析】'.length).trim() : '';

        // 教材溯源拆分："第10章 波动 - 10.6 波的干涉"
        const cm = chapterRaw.match(/^(.*?章[^-–—]*?)\s*[-–—]\s*(.+)$/);
        const chapter = cm ? { label: cm[1].trim(), section: cm[2].trim(), raw: chapterRaw }
                           : { label: chapterRaw, section: '', raw: chapterRaw };

        // 卷名 / 题号：从来源里拆 "25261 大学物理1B B卷 T3"
        const tm = source.match(/^(.*?)\s*T(\d+)\s*$/);
        const paper = tm ? tm[1].trim() : source;
        const num = tm ? parseInt(tm[2], 10) : 0;

        // 选项提取：以 A.~D. 开头的行
        const lines = body.split('\n');
        const options = [];
        const descLines = [];
        for (const line of lines) {
            const om = line.match(/^\s*([A-D])[.、．]\s*(.+)$/);
            if (om) {
                options.push({ letter: om[1], text: om[2].trim() });
            } else {
                descLines.push(line);
            }
        }
        const desc = descLines.join('\n').trim();
        const type = options.length >= 2 ? 'choice' : 'open';
        const subtype = type === 'open' && /_+|＿+|（\s*）/.test(body) ? 'fill' : 'calc';

        // 图片收集（正文+选项+解析）
        const allText = [desc, ...options.map(o => o.text), analysis].join('\n');
        const images = [...allText.matchAll(/!\[[^\]]*\]\((images\/[^)\s]+)\)/g)].map(m => m[1]);

        questions.push({
            id: `${fileId}-T${num}`,
            fileId, source, paper, num,
            chapter, type, subtype,
            desc, options,
            images: [...new Set(images)],
            answer, analysis
        });
    }
    return questions;
}

// ─── 主流程 ───
function main() {
    if (!existsSync(SRC_DIR)) {
        console.error(`源目录不存在: ${SRC_DIR}`);
        console.error('请把一年一卷的 MD 文件放入 physics-quiz/source/，图片放 source/images/');
        process.exit(1);
    }
    let files = readdirSync(SRC_DIR).filter(f => f.endsWith('.md') && f !== NOTES_FILE).sort();

    // 必备知识（可选文件，缺失时章节训练不显示必备知识项）
    const notesPath = join(SRC_DIR, NOTES_FILE);
    const notes = existsSync(notesPath) ? parseNotes(readFileSync(notesPath, 'utf8')) : {};
    if (only) files = files.filter(f => f.startsWith(only));
    if (!files.length) { console.error(`source/ 下没有 MD 文件${only ? `（--only ${only}）` : ''}`); process.exit(1); }

    mkdirSync(IMG_OUT, { recursive: true });
    const all = [];
    let imgCopied = 0, imgMissing = 0;

    for (const f of files) {
        const fileId = f.replace(/\.md$/, '');
        const text = readFileSync(join(SRC_DIR, f), 'utf8');
        const qs = parseFile(text, fileId);
        console.log(`✔ ${f}: ${qs.length} 题`);

        for (const q of qs) {
            for (const img of q.images) {
                const from = join(SRC_DIR, img);
                const to = join(IMG_OUT, basename(img));
                if (existsSync(from)) {
                    copyFileSync(from, to); imgCopied++;
                } else if (!existsSync(to)) {
                    console.warn(`  ⚠ 图片缺失: ${img}`); imgMissing++;
                }
            }
        }
        all.push(...qs);
    }

    const data = {
        meta: { subject: '大学物理', version: 3, builtAt: new Date().toISOString(), files },
        textbook: { sections: TEXTBOOK_SECTIONS, notes },
        questions: all
    };
    writeFileSync(join(OUT_DIR, 'physics-data.json'), JSON.stringify(data, null, 1), 'utf8');

    const chapters = [...new Set(all.map(q => q.chapter.label))].length;
    const papers = [...new Set(all.map(q => q.paper))].length;
    console.log(`\n完成: ${all.length} 题 / ${papers} 套卷 / ${chapters} 章 / 必备知识 ${Object.keys(notes).length} 章`);
    // 溯源一致性提示：题目溯源节不在教材结构中的，疑似分类错误
    for (const q of all) {
        const secs = TEXTBOOK_SECTIONS[q.chapter.label];
        if (secs && q.chapter.section && !secs.includes(q.chapter.section)) {
            console.warn(`  ⚠ 溯源小节不在教材结构中: ${q.id} → ${q.chapter.raw}`);
        }
    }
    console.log(`图片: 复制 ${imgCopied}，缺失 ${imgMissing}`);
    console.log(`输出: ${join(OUT_DIR, 'physics-data.json')}`);
}

main();
