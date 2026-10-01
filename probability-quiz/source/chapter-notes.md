# 各章必备知识（依据《概率论与数理统计讲义》天津大学 提炼）

【必备知识】第1章 随机事件与概率
## 1.1 随机事件及运算
- 样本空间 $\Omega$：随机试验所有可能结果的全体；事件是 $\Omega$ 的子集。
- 事件关系：包含 $A\subset B$、和 $A\cup B$、积 $AB$、差 $A-B=A\overline{B}$、互斥 $AB=\varnothing$、对立 $\overline{A}$（$A\cup\overline{A}=\Omega$ 且 $A\overline{A}=\varnothing$）。
- 德摩根律：$\overline{A\cup B}=\overline{A}\ \overline{B}$，$\overline{AB}=\overline{A}\cup\overline{B}$（可推广到任意多个）。
- 分配律：$A(B\cup C)=AB\cup AC$，$A\cup BC=(A\cup B)(A\cup C)$。
## 1.2 概率及性质
- 概率公理：非负性、规范性 $P(\Omega)=1$、可列可加性。
- 加法公式：$P(A\cup B)=P(A)+P(B)-P(AB)$；三事件 $P(A\cup B\cup C)=\sum P-\sum P(\text{两两交})+P(ABC)$。
- $P(A-B)=P(A)-P(AB)$；$P(\overline{A})=1-P(A)$；单调性 $A\subset B\Rightarrow P(A)\leq P(B)$。
- 差事件化简常用：$P(A\overline{B})=P(A)-P(AB)$。
## 1.3 古典概型和几何概型
- 古典概型：$P(A)=\dfrac{A\text{ 包含的样本点数}}{\text{样本点总数}}$；计数用排列组合（不放回抽取用组合数 $C_n^k$）。
- 几何概型：概率 = 有利区域测度 / 总区域测度（长度、面积）；如"两数之和/积满足条件"在单位正方形内算面积。
- 配对、分房、抽球（有/无放回）是典型模型；"至少"问题优先用补集。
## 1.4 条件概率与乘法公式
- 条件概率 $P(B|A)=\dfrac{P(AB)}{P(A)}$；乘法公式 $P(AB)=P(A)P(B|A)$。
- 全概率公式：若 $B_1,\cdots,B_n$ 为完备事件组，$P(A)=\sum_i P(B_i)P(A|B_i)$。
- 贝叶斯公式：$P(B_k|A)=\dfrac{P(B_k)P(A|B_k)}{\sum_i P(B_i)P(A|B_i)}$；$P(B_i)$ 为先验概率，$P(B_k|A)$ 为后验概率。
- 典型应用：产品检验（次品率）、疾病诊断（发病率与确诊率）、信号传输。
## 1.5 独立性
- $A$ 与 $B$ 独立 $\Leftrightarrow P(AB)=P(A)P(B)$；此时 $A$ 与 $\overline{B}$、$\overline{A}$ 与 $B$、$\overline{A}$ 与 $\overline{B}$ 均独立。
- 互斥且概率均正的事件必不独立；独立与互斥一般不能同时成立。
- 多事件两两独立 $\ne$ 相互独立：相互独立还要求任意多个事件的积的概率等于概率之积。
- 伯努利试验：$n$ 重独立试验中事件发生 $k$ 次的概率 $C_n^k p^k(1-p)^{n-k}$。

【必备知识】第2章 随机变量及分布
## 2.1 随机变量及分布函数
- 分布函数 $F(x)=P\{X\leq x\}$：单调不减、右连续、$F(-\infty)=0,F(+\infty)=1$。
- $P\{a<X\leq b\}=F(b)-F(a)$；$P\{X=a\}=F(a)-F(a-0)$（跳跃高度即原子概率）。
- 分布函数连续 $\Rightarrow$ 连续型或混合型中无原子；有跳跃点则含离散成分。
## 2.2 离散型随机变量的分布
- 分布律 $P\{X=x_k\}=p_k$，$\sum p_k=1$；$F(x)=\sum_{x_k\leq x}p_k$（阶梯函数）。
- 常用分布：0-1 分布 $B(1,p)$；二项 $B(n,p)$：$E=np,D=np(1-p)$；泊松 $P(\lambda)$：$E=D=\lambda$，$P\{X=k\}=\dfrac{\lambda^k}{k!}e^{-\lambda}$；几何分布 $P\{X=k\}=p(1-p)^{k-1}$：$E=1/p,D=(1-p)/p^2$。
- 泊松定理：$n$ 大 $p$ 小时 $B(n,p)$ 用 $P(np)$ 近似。
## 2.3 连续型随机变量的分布
- 概率密度 $f(x)\geq0$，$\int_{-\infty}^{+\infty}f=1$；$F(x)=\int_{-\infty}^{x}f(t)\mathrm{d}t$，$P\{a<X\leq b\}=\int_a^b f$；连续型 $P\{X=a\}=0$。
- 由 $F$ 求 $f$：在连续点 $f=F'$；由 $f$ 定常数用归一化 $\int f=1$。
- 常用分布：均匀 $U(a,b)$：$f=\dfrac{1}{b-a}$，$E=\dfrac{a+b}{2},D=\dfrac{(b-a)^2}{12}$；指数 $\mathrm{Exp}(\lambda)$：$f=\lambda e^{-\lambda x}(x>0)$，$E=1/\lambda,D=1/\lambda^2$，无记忆性 $P\{X>s+t|X>s\}=P\{X>t\}$；正态 $N(\mu,\sigma^2)$：密度关于 $\mu$ 对称，$P\{X\leq x\}=\Phi\left(\dfrac{x-\mu}{\sigma}\right)$。
- 标准正态性质：$\Phi(-x)=1-\Phi(x)$；$3\sigma$ 准则。
## 2.4 随机变量函数的分布
- 离散型：$Y=g(X)$ 逐值合并概率。
- 连续型一维：分布函数法 $F_Y(y)=P\{g(X)\leq y\}$ 对 $y$ 求导；单调可导函数用公式 $f_Y(y)=f_X(h(y))|h'(y)|$（$h$ 为反函数）。
- 注意分段：$Y=X^2$、$Y=|X|$ 类用 $F_Y(y)=P\{-\sqrt{y}\leq X\leq\sqrt{y}\}$；分段密度逐段积分。

【必备知识】第3章 多维随机变量及分布
## 3.1 联合分布函数与边缘分布函数
- 联合分布函数 $F(x,y)=P\{X\leq x,Y\leq y\}$；边缘 $F_X(x)=F(x,+\infty)$。
- 矩形区域概率：$P\{x_1<X\leq x_2,y_1<Y\leq y_2\}=F(x_2,y_2)-F(x_1,y_2)-F(x_2,y_1)+F(x_1,y_1)$。
- $\max$/$\min$：独立时 $F_{\max}=F_X F_Y$，$F_{\min}=1-(1-F_X)(1-F_Y)$。
## 3.2 二维离散型随机变量及分布
- 联合分布律 $p_{ij}=P\{X=x_i,Y=y_j\}$；边缘律按行/列求和。
- 条件分布律 $P\{X=x_i|Y=y_j\}=\dfrac{p_{ij}}{p_{\cdot j}}$。
- 独立性：所有格点 $p_{ij}=p_{i\cdot}p_{\cdot j}$；由部分格点与边缘律反推联合律是常见题型（配合 $P\{XY=0\}=1$ 等条件定零格点）。
## 3.3 二维连续型随机变量及分布
- 联合密度 $f(x,y)\geq0$，$\iint f=1$；$F(x,y)=\int_{-\infty}^{x}\int_{-\infty}^{y}f\,\mathrm{d}u\mathrm{d}v$；区域概率 = 区域上二重积分。
- 边缘密度：$f_X(x)=\int_{-\infty}^{+\infty}f(x,y)\mathrm{d}y$，积分限由支撑域决定（常需分段）。
- 条件密度 $f_{X|Y}(x|y)=\dfrac{f(x,y)}{f_Y(y)}$（$f_Y(y)>0$）；条件概率 = 对条件密度积分。
- 独立性：$f(x,y)=f_X(x)f_Y(y)$（支撑域须为矩形区域才可独立）。
- 二维均匀分布：密度 = 1/区域面积；二维正态 $(\mu_1,\mu_2;\sigma_1^2,\sigma_2^2;\rho)$：$\rho=0\Leftrightarrow$ 独立，边缘仍正态，线性组合仍正态。
## 3.4 二维随机变量函数的分布
- $Z=X+Y$（独立）卷积公式：$f_Z(z)=\int_{-\infty}^{+\infty}f_X(x)f_Y(z-x)\mathrm{d}x$；一般情形 $F_Z(z)=\iint_{x+y\leq z}f\,\mathrm{d}x\mathrm{d}y$ 对 $z$ 求导。
- $Z=\max(X,Y)$、$\min(X,Y)$：独立时分别用 $F_XF_Y$、$1-(1-F_X)(1-F_Y)$；否则按区域积分。
- $Z=XY$、$X/Y$、$2X-Y$ 等：先求 $F_Z(z)=P\{g(X,Y)\leq z\}$ 的积分区域，再对 $z$ 求导，注意分段点由直线扫过支撑域顶点产生。

【必备知识】第4章 随机变量的数字特征
## 4.1 随机变量的数学期望
- 离散 $E(X)=\sum x_k p_k$；连续 $E(X)=\int x f(x)\mathrm{d}x$（要求绝对收敛）。
- 性质：线性性 $E(aX+bY)=aE(X)+bE(Y)$（无条件成立）；独立时 $E(XY)=E(X)E(Y)$。
- 随机变量函数的期望：$E[g(X)]=\sum g(x_k)p_k$ 或 $\int g(x)f(x)\mathrm{d}x$（不必先求 $Y=g(X)$ 的分布）。
- 常用分布期望：$B(n,p):np$；$P(\lambda):\lambda$；$U(a,b):\frac{a+b}{2}$；$\mathrm{Exp}(\lambda):1/\lambda$；$N(\mu,\sigma^2):\mu$。
## 4.2 随机变量的方差
- $D(X)=E(X^2)-[E(X)]^2$；$D(aX+b)=a^2D(X)$；独立时 $D(X+Y)=D(X)+D(Y)$。
- 一般地 $D(X\pm Y)=D(X)+D(Y)\pm2\mathrm{Cov}(X,Y)$。
- 常用分布方差：$B(n,p):np(1-p)$；$P(\lambda):\lambda$；$U(a,b):\frac{(b-a)^2}{12}$；$\mathrm{Exp}(\lambda):1/\lambda^2$；$N(\mu,\sigma^2):\sigma^2$。
- 切比雪夫不等式：$P\{|X-E(X)|\geq\varepsilon\}\leq\dfrac{D(X)}{\varepsilon^2}$。
## 4.3 随机变量的协方差与相关系数
- $\mathrm{Cov}(X,Y)=E(XY)-E(X)E(Y)$；$\mathrm{Cov}(X,Y)=\rho_{X,Y}\sqrt{D(X)}\sqrt{D(Y)}$。
- 不相关 $\Leftrightarrow\mathrm{Cov}=0\Leftrightarrow\rho=0\Leftrightarrow D(X+Y)=D(X)+D(Y)$；独立 $\Rightarrow$ 不相关，反之不然（二维正态中两者等价）。
- 性质：双线性、对称性；$\mathrm{Cov}(X,X)=D(X)$；$D(X\pm Y)=D(X)+D(Y)\pm2\mathrm{Cov}$。
- $|\rho|\leq1$；$|\rho|=1\Leftrightarrow X,Y$ 线性相关。
## 4.4 矩与协方差矩阵
- $k$ 阶原点矩 $E(X^k)$、中心矩 $E[(X-E(X))^k]$；$E(X^2)=D(X)+[E(X)]^2$ 是换算核心。
- 正态分布四阶矩：$X\sim N(\mu,\sigma^2)$ 时 $E[(X-\mu)^4]=3\sigma^4$。

【必备知识】第5章 大数定律和中心极限定理
## 5.1 切比雪夫不等式
- $P\{|X-\mu|\geq\varepsilon\}\leq\dfrac{\sigma^2}{\varepsilon^2}$，$P\{|X-\mu|<\varepsilon\}\geq1-\dfrac{\sigma^2}{\varepsilon^2}$。
- 应用：估计概率下界/上界；先算 $E$ 与 $D$，再配方 $|X-\mu|$ 的形式。
## 5.2 大数定律
- 辛钦大数定律：独立同分布且期望存在时 $\dfrac{1}{n}\sum X_i\xrightarrow{P}E(X)$。
- 伯努利大数定律：频率依概率收敛于概率。
- 切比雪夫大数定律：独立、方差一致有界即成立。
- 收敛目标计算：如 $\frac{1}{n}\sum g(X_i)\xrightarrow{P}E[g(X)]$。
## 5.3 中心极限定理
- 列维—林德伯格：独立同分布、$E=\mu,D=\sigma^2$ 时 $\dfrac{\sum X_i-n\mu}{\sqrt{n}\sigma}\xrightarrow{d}N(0,1)$。
- 棣莫弗—拉普拉斯：$X\sim B(n,p)$ 时 $\dfrac{X-np}{\sqrt{np(1-p)}}\xrightarrow{d}N(0,1)$。
- 应用三步：算总和的均值与方差 → 标准化 → 查 $\Phi$；注意区分"总和"与"平均值"的标准化形式。

【必备知识】第6章 数理统计的基本概念与抽样分布
## 6.1 基本概念
- 总体、样本、样本观测值；经验分布函数 $F_n(x)$ = 样本中不超过 $x$ 的频率。
- 样本均值 $\bar{X}=\frac{1}{n}\sum X_i$，样本方差 $S^2=\dfrac{1}{n-1}\sum(X_i-\bar{X})^2$（分母 $n-1$ 才无偏）。
- $E(\bar{X})=\mu$，$D(\bar{X})=\sigma^2/n$，$E(S^2)=\sigma^2$。
## 6.2 统计量及分布
- 统计量：不含未知参数的样本函数。
- $\chi^2$ 分布：$\chi^2=\sum_{i=1}^n Z_i^2$（$Z_i$ 独立标准正态），自由度 $n$，$E=n,D=2n$。
- $t$ 分布：$T=\dfrac{Z}{\sqrt{\chi^2_n/n}}$，自由度 $n$，关于 0 对称。
- $F$ 分布：$F=\dfrac{\chi^2_m/m}{\chi^2_n/n}$，自由度 $(m,n)$；$1/F\sim F(n,m)$。
- 正态总体抽样分布：$\dfrac{(n-1)S^2}{\sigma^2}\sim\chi^2(n-1)$；$\dfrac{\bar{X}-\mu}{S/\sqrt{n}}\sim t(n-1)$；$\bar{X}$ 与 $S^2$ 独立；两个独立正态样本的方差比服从 $F$。
- 构造分布的套路：配标准正态平方 → $\chi^2$；两独立 $\chi^2$ 各除自由度相除 → $F$；标准正态除以 $\sqrt{\chi^2/\text{自由度}}$ → $t$。

【必备知识】第7章 参数估计
## 7.1 参数的点估计
- 矩估计：令样本矩 = 总体矩（一个参数用一阶矩 $E(X)=\bar{X}$，必要时用二阶矩），解出参数。
- 最大似然估计（MLE）：似然函数 $L=\prod f(x_i;\theta)$ → 取对数 → 对参数求导令为 0 解出；单调似然在边界取最值（如均匀分布上界 $\hat{\theta}=X_{(n)}$、下界 $\hat{\theta}=X_{(1)}$）。
- 常见结论：指数/正态均值 $\hat{\mu}=\bar{X}$；二项/泊松比例 $\hat{p}=\bar{X}$（或频率）；帕累托类 $\hat{\theta}=\dfrac{n}{\sum\ln X_i}$ 型。
## 7.2 估计量的优良性准则
- 无偏性 $E(\hat{\theta})=\theta$；线性组合无偏 $\Leftrightarrow$ 系数和为 1。
- 有效性：同为无偏时方差小者更有效；$\bar{X}$ 比单个 $X_1$ 有效。
- 相合性（一致性）：$\hat{\theta}_n\xrightarrow{P}\theta$；无偏且方差趋于 0 即相合。
- 注意：$f(\hat{\theta})$ 一般不是 $f(\theta)$ 的无偏估计（除非 $f$ 为线性）。
## 7.3 区间估计
- 枢轴量法：构造含待估参数、分布已知的量，反解出参数的区间。
- $\sigma^2$ 已知，$\mu$ 的双侧置信区间：$\bar{X}\pm z_{\alpha/2}\dfrac{\sigma}{\sqrt{n}}$。
- $\sigma^2$ 未知，$\mu$ 的双侧置信区间：$\bar{X}\pm t_{\alpha/2}(n-1)\dfrac{S}{\sqrt{n}}$；单侧下限把 $z_{\alpha/2}$ 换成 $z_\alpha$（或 $t_\alpha$）。
- $\sigma^2$ 的置信区间：$\left(\dfrac{(n-1)S^2}{\chi^2_{\alpha/2}(n-1)},\dfrac{(n-1)S^2}{\chi^2_{1-\alpha/2}(n-1)}\right)$（上侧分位数记号）；单侧置信上限为 $\dfrac{(n-1)S^2}{\chi^2_{1-\alpha}(n-1)}$。
- 两个正态总体均值差（方差已知）：$(\bar{X}-\bar{Y})\pm z_{\alpha/2}\sqrt{\sigma_1^2/n_1+\sigma_2^2/n_2}$。

【必备知识】第8章 假设检验
## 8.1 假设检验的基本概念
- 原假设 $H_0$ 与备择假设 $H_1$；显著性水平 $\alpha$ = $H_0$ 为真时拒绝 $H_0$ 的概率（第一类错误"弃真"）。
- 第二类错误"取伪"：$H_0$ 不真却接受；拒绝 $H_0$ 且不犯错误 = $H_0$ 不真且拒绝。
- 拒绝域由显著性水平确定；单侧检验看单尾分位数，双侧看 $\alpha/2$。
## 8.2 正态总体参数的假设检验
- $\mu$ 检验（$\sigma^2$ 已知，$U$ 检验）：$U=\dfrac{\bar{X}-\mu_0}{\sigma/\sqrt{n}}$；双侧拒绝域 $|U|>z_{\alpha/2}$，右尾 $U>z_\alpha$，左尾 $U<-z_\alpha$。
- $\mu$ 检验（$\sigma^2$ 未知，$t$ 检验）：$T=\dfrac{\bar{X}-\mu_0}{S/\sqrt{n}}\sim t(n-1)$；自由度 $n-1$。
- $\sigma^2$ 检验（$\chi^2$ 检验）：$\chi^2=\dfrac{(n-1)S^2}{\sigma_0^2}\sim\chi^2(n-1)$；双侧拒绝域 $\chi^2\geq\chi^2_{\alpha/2}$ 或 $\chi^2\leq\chi^2_{1-\alpha/2}$。
- 两个正态总体：均值差用 $U$/$t$ 统计量（方差相等时用合并方差 $S_w^2=\dfrac{(n_1-1)S_1^2+(n_2-1)S_2^2}{n_1+n_2-2}$，自由度 $n_1+n_2-2$）；方差比用 $F=\dfrac{S_1^2}{S_2^2}\sim F(n_1-1,n_2-1)$。
- 检验流程：提出假设 → 选统计量 → 定拒绝域 → 代入观测值比较 → 下结论。
