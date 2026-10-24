# 开发约定

- 保持原生 HTML/CSS/JavaScript、Python 标准库后端和原生 Java Android 壳。
- `exam` 负责网页题库和答题功能、保留经过确认的题目修正，并按需向 `zhenti-pipeline-v2` 提供题库数据。
- 完整 PDF 题册、附图处理、多选题排版、来源解析、统一目录和连续页码均归 `zhenti-pipeline-v2`。迁入的 PDF 文件仅作历史交接资料，不列入 `exam` 待办，也不在本项目继续开发 PDF 生成流程。
- 各科页面的源文件是 `web/exam/{marx,physics,probability}.html`；题库 JSON 也内嵌于这些页面。
- `web/index.html` 维护主壳与增强层。各科页面修改后，运行 `python3 tools/build_frontend.py` 更新其中的 Base64 payload；不要手工编辑 payload。
- `bank-data/` 是离线快照，用 `python3 tools/extract_bank.py` 显式刷新。个人 `data/` 中的修正和 `bank-data-export/` 中的历史导出不自动合并到题库。
- `config.json`、`web/config.local.js`、`data/`、`.local/`、签名凭证和构建产物不提交。不要打印真实令牌或模型密钥。浏览器配置只能放应用访问令牌，模型密钥仅存服务端。
- 前端构建会写入 `web/`。验证构建脚本时优先通过 `--web-dir`、`--exam-dir`、`--out` 使用临时目录。
- 运行 `python3 -m unittest discover -s tests -v` 验证后端与前端配置；前端行为测试需要 Node.js。测试不使用真实 AI 服务或个人数据。
- 题库交接使用 `tools/extract_bank.py --out <导出目录>`，保留题目 ID、题型、来源与附图数据；不自动合并个人 `corr`，不导出私人备注、作答记录或密钥。职责与数据约定见 `docs/data-handoff.md`。
- 第三方代码和字体保留原版权与许可证，见 `THIRD_PARTY_NOTICES.md`。
