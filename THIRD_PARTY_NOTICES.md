# 第三方组件与题库内容

根目录的 MIT 许可证适用于本项目原创程序代码。下列第三方代码、字体以及题库内容保留各自的权利与许可，不因存放在本仓库而改用 MIT。

## 前身项目

本项目承接 [TJU-Quiz-Hub](https://github.com/WhatYearIsNow/TJU-Quiz-Hub)，该项目采用 MIT。根目录 `LICENSE` 保留其原版权声明；旧提交与分支的保存方式见 [项目沿革](https://github.com/WhatYearIsNow/exam/blob/main/docs/history.md)。

## 前端公式渲染

- **KaTeX 0.16.15**：大学物理与概率论页面内嵌公式渲染代码，原项目采用 MIT。完整许可见 [licenses/KaTeX-MIT.txt](licenses/KaTeX-MIT.txt)，上游为 [KaTeX v0.16.15](https://github.com/KaTeX/KaTeX/tree/v0.16.15)。
- **KaTeX 字体**：页面内嵌的字体适用 SIL Open Font License 1.1，含 Design Science 与 Khan Academy 的版权及保留字体名。完整声明与许可见 [licenses/KaTeX-fonts-OFL.txt](licenses/KaTeX-fonts-OFL.txt)，源字体见 [上游 fonts 目录](https://github.com/KaTeX/KaTeX/tree/v0.16.15/fonts)。

## PDF 排版组件

| 组件 | 本地位置 | 许可与来源 |
| --- | --- | --- |
| exam-zh 0.3.6 | `vendor/exam-zh/` | LaTeX Project Public License 1.3c，见目录内 `LICENSE`；[完整上游项目](https://github.com/xkwxdyy/exam-zh/tree/v0.3.6) |
| ulem，2019-11-18 版 | `vendor/ulem/` | Donald Arseneau 的原许可，见 `LICENSE` 及 `ulem.sty` 文件头；[CTAN ulem](https://ctan.org/pkg/ulem) |
| STIX Two 2.12 b168 | `vendor/STIXTwo/` | SIL Open Font License 1.1，见 `OFL.txt`、`AUTHORS.txt`、`CONTRIBUTORS.txt`；[上游 STIX Fonts](https://github.com/stipub/stixfonts/tree/v2.12) |
| Asana Math 000.962 | `vendor/Asana-Math/` | SIL Open Font License 1.1，见 `OFL.txt`；版权与完整许可也保留在原字体元数据中；[CTAN Asana-Math](https://ctan.org/pkg/asana-math) |

这些第三方程序与字体保留迁移前的内容。`vendor/exam-zh/` 是运行所需组件的副本，完整源项目及其他文件请从上游取得；本项目不代表上游作者提供支持。TeX Live、Android SDK 和 JDK 属于外部运行或构建依赖，未将其安装目录纳入仓库。

## 题库、试卷与图片

`web/exam/*.html`、首页内嵌页面及 `bank-data/*.json` 含题目、答案、解析、教材章节和部分图片。题目的 `source`、`paper` 等字段保留现有来源信息。本次目录迁移没有重新确认每份原始材料的再分发授权；这些内容不纳入本项目原创代码的 MIT 授权范围。公开发布题库或相关 PDF 前，应另行核实对应内容的来源与授权。

个人作答记录、备注、AI 结论和手动修正存放在本地 `data/`；历史导出与下载资料也单独保留，不作为本次开源代码的一部分提交。

题库材料、人工修正与程序许可的区别，以及来源核实方式，见 [题库来源与授权说明](https://github.com/WhatYearIsNow/exam/blob/main/docs/content-rights.md)。
