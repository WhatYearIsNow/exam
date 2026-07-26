"use client";

import { useState } from "react";

const banks = [
  {
    id: "history-264",
    short: "史纲 · 25262版",
    name: "中国近现代史纲要",
    detail: "264 题 · 单选与多选",
    count: "264",
    tone: "blue",
  },
  {
    id: "history-178",
    short: "史纲 · 精简版",
    name: "中国近现代史纲要",
    detail: "178 题 · 高频知识点",
    count: "178",
    tone: "ink",
  },
  {
    id: "cs-python-100",
    short: "计算机基础",
    name: "Python 程序设计",
    detail: "100 题 · 代码与基础概念",
    count: "100",
    tone: "lime",
  },
];

export function BankPicker() {
  const [selected, setSelected] = useState(banks[0]);

  return (
    <div className="picker-shell">
      <div className="picker-list" role="list" aria-label="可用题库">
        {banks.map((bank, index) => (
          <button
            className={`bank-row ${selected.id === bank.id ? "is-selected" : ""}`}
            key={bank.id}
            onClick={() => setSelected(bank)}
            type="button"
            aria-pressed={selected.id === bank.id}
          >
            <span className={`bank-index bank-index--${bank.tone}`}>0{index + 1}</span>
            <span className="bank-copy">
              <strong>{bank.short}</strong>
              <span>{bank.detail}</span>
            </span>
            <span className="bank-count" aria-label={`${bank.count} 道题`}>
              {bank.count}
              <small>题</small>
            </span>
          </button>
        ))}
      </div>

      <div className="picker-action">
        <div>
          <span className="eyebrow">已选择</span>
          <strong>{selected.name}</strong>
          <p>记录保存在当前设备，无需注册。</p>
        </div>
        <a className="button button--primary" href={`/quiz.html?bank=${selected.id}`}>
          开始刷题 <span aria-hidden="true">→</span>
        </a>
      </div>
    </div>
  );
}
