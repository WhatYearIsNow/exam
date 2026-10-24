# 真题分类汇编与离线包

按教材章节生成 exam-zh / XeLaTeX 排版的 PDF。下列命令从源码仓库根目录，或离线包解压后的 `exam-compilation/` 目录执行。

## 环境与生成

Python 工具只使用标准库。检查题库和生成 `.tex` 无需 LaTeX；编译 PDF 需要含 XeLaTeX、ctex/Fandol、Latin Modern 等组件的 TeX Live。macOS 可使用 MacTeX，Windows 可使用 TeX Live。Debian/Ubuntu 可安装：

```bash
sudo apt install texlive-xetex texlive-latex-extra texlive-lang-chinese texlive-fonts-recommended
```

macOS / Linux 下，补装包内缺少的 exam-zh、ulem 和数学字体：

```bash
bash tools/setup_tex.sh
python3 tools/make_book.py --subject probability --inspect
python3 tools/make_book.py --subject probability --chapter 1 --build
```

安装脚本只向 TeX Live 用户树 `TEXMFHOME` 补装缺失组件。Windows 可用 `kpsewhich -var-value=TEXMFHOME` 查找用户树，将 `vendor/exam-zh/`、`vendor/ulem/` 复制到其中的 `tex/latex/`，将 STIXTwo 和 Asana-Math 的 `.otf` 文件放入 `fonts/opentype/` 下相应子目录，然后运行 `mktexlsr`。

默认精选打样，每节最多 4 题并保留解答题，产物为 `book/probability-ch1-sample.tex` 和 `.pdf`。添加 `--all` 收录整章可用题，文件名为 `book/probability-ch1.tex` 和 `.pdf`。不加 `--build` 只生成 TeX；`--out` 可指定输出目录。

生成器检查答案、解析、题型和来源，并核对收录题数、题目环境、解析条数、来源行数是否一致。数据预检或一致性校验失败时不会写入新 TeX；LaTeX 编译失败时可能留下 TeX 与日志，需检查输出目录。

题目区不带来源标签；来源列于每题解析之后。个人存疑、备注和 AI 标注不呈现。当前按章输出，结构包括凡例、知识提要、按节分组的题目、选择题答案速查和解析。

## 数据与打包

仓库以 `web/exam/*.html` 内嵌 JSON 为题库来源。HTML 缺失时，生成器才回退到 `bank-data/*.json` 快照；也可用 `--exam-dir` 或 `ILOVETJU_EXAM_DIR` 指定 HTML 所在目录。

在源码仓库根目录刷新快照并生成离线 ZIP：

```bash
python3 tools/extract_bank.py
python3 tools/package_offline.py
# 默认输出 book/exam-compilation.zip；可用 --out 指定 ZIP 文件路径。
```

打包不会自动更新快照或修改网页。离线包只带两份生成/提取脚本、安装脚本、三科快照、第三方组件和许可说明，不含 `web/`、服务端配置或 `data/` 个人记录。解压后即从快照读取，无需启动网站。包内 `extract_bank.py` 仅在另有 HTML 来源并通过 `--exam-dir` 指定时使用。

原创代码采用 MIT；题库和第三方组件分别适用自身的授权条件，详见包内 `THIRD_PARTY_NOTICES.md` 和 `licenses/`。

## 已知限制

- 目前仅概率论配置了 `MOCK_SOURCE`，马原和物理可检查题库，生成 PDF 前须补充真实来源配置。
- 物理题的内嵌 base64 图片尚未接入 PDF 插图流程，不能保证图题完整排版。
- 尚不支持把所有章节合成一本 PDF。
- `bank-data-export/` 的历史修正及个人 `corr` 记录不自动合并；离线包反映的是打包时的 `bank-data/` 快照。
