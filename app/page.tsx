import { BankPicker } from "./BankPicker";

const featureItems = [
  ["01", "按章节练", "把整门课拆开，一章一章清掉盲区。"],
  ["02", "模拟考试", "按题型比例随机组卷，提前进入考试节奏。"],
  ["03", "错题回炉", "自动收录错题，集中重练，直到真正掌握。"],
  ["04", "进度不断", "自动保存作答现场，关掉页面也能接着练。"],
];

export default function Home() {
  return (
    <main>
      <div className="grain" aria-hidden="true" />

      <header className="site-header wrap">
        <a className="brand" href="#top" aria-label="TJU Quiz Hub 首页">
          <span className="brand-mark">T</span>
          <span>
            <strong>TJU QUIZ HUB</strong>
            <small>天大刷题站</small>
          </span>
        </a>
        <nav aria-label="主导航">
          <a href="#banks">选题库</a>
          <a href="#features">功能</a>
          <a className="nav-cta" href="/quiz.html?bank=history-264">
            直接开刷
          </a>
        </nav>
      </header>

      <section className="hero wrap" id="top">
        <div className="hero-copy">
          <div className="status-pill">
            <span /> 3 套题库 · 542 道题
          </div>
          <p className="kicker">BEIYANG STUDY TOOL · 2026</p>
          <h1>
            把碎片时间，
            <span>练成确定的分数。</span>
          </h1>
          <p className="hero-lead">
            为天大学生准备的轻量刷题站。章节练习、模拟组卷、错题回顾，
            从第一次翻书到走进考场，都有清晰进度。
          </p>
          <div className="hero-actions">
            <a className="button button--primary" href="#banks">
              选择一门课 <span aria-hidden="true">↓</span>
            </a>
            <span className="microcopy">不登录 · 不收费 · 打开即用</span>
          </div>
        </div>

        <div className="quiz-demo" aria-label="答题界面预览">
          <div className="demo-topline">
            <span>中国近现代史纲要</span>
            <span>12 / 60</span>
          </div>
          <div className="demo-progress"><span /></div>
          <div className="demo-type">单项选择</div>
          <h2>近代中国睁眼看世界的第一人是？</h2>
          <div className="demo-options">
            <div><span>A</span> 魏源</div>
            <div className="chosen"><span>B</span> 林则徐 <b>✓</b></div>
            <div><span>C</span> 康有为</div>
            <div><span>D</span> 严复</div>
          </div>
          <div className="demo-foot">
            <span>答对了，继续保持</span>
            <span>Enter 下一题 →</span>
          </div>
          <div className="demo-stamp" aria-hidden="true">TJU</div>
        </div>
      </section>

      <section className="bank-section" id="banks">
        <div className="wrap">
          <div className="section-heading">
            <div>
              <p className="kicker">COURSE BANKS</p>
              <h2>选一门，现在开刷。</h2>
            </div>
            <p>先完成一组，再考虑下一组。<br />开始本身就是进度。</p>
          </div>
          <BankPicker />
        </div>
      </section>

      <section className="features wrap" id="features">
        <div className="section-heading section-heading--dark">
          <div>
            <p className="kicker">STUDY LOOP</p>
            <h2>每一次作答，<br />都沉淀成下一次的把握。</h2>
          </div>
          <div className="loop-note">
            <span>练习</span><i>→</i><span>复盘</span><i>→</i><span>再练</span>
          </div>
        </div>

        <div className="feature-grid">
          {featureItems.map(([number, title, copy]) => (
            <article key={number}>
              <span className="feature-number">{number}</span>
              <h3>{title}</h3>
              <p>{copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="closing">
        <div className="wrap closing-inner">
          <div>
            <span className="closing-mark">T</span>
            <p className="kicker">FROM PEIYANG TO EVERY EXAM ROOM</p>
            <h2>今天练过的题，<br />会在考场上替你托底。</h2>
          </div>
          <a className="round-link" href="/quiz.html?bank=history-264">
            <span>开始<br />刷题</span>
            <b aria-hidden="true">↗</b>
          </a>
        </div>
      </section>

      <footer className="site-footer wrap">
        <div className="brand brand--footer">
          <span className="brand-mark">T</span>
          <span><strong>TJU QUIZ HUB</strong><small>开源 · 本地优先</small></span>
        </div>
        <p>为学习而做，与天津大学官方无隶属关系。</p>
        <a href="https://github.com/WhatYearIsNow/TJU-Quiz-Hub" target="_blank" rel="noreferrer">
          GitHub ↗
        </a>
      </footer>
    </main>
  );
}
