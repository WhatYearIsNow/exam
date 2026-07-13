// 题库元信息
const QUIZ_META = {
    subject: "计算机软件技术基础",
    version: "Python题库",
    totalQuestions: 100,
    campusName: "北洋校歌"
};

const questionData = [
            // 第001题
            {
                title: "【单项选择题001】",
                desc: "下列程序的输出是（　　）",
                code: `for x in range(1,10):    
	if x % 2 !=0:        
		continue             
	print(x, end=' ')`,
                options: [
                    "A. 1 3 5 7 9",
                    "B. 2 4 6 8 10",
                    "C. 2 4 6 8",
                    "D. 1 3 5 7"
                ],
                answer: "C",
                analysis: "range(1,10)生成1-9的整数，当x为奇数时执行continue跳过print，只打印偶数2、4、6、8。"
            },
            // 第002题
            {
                title: "【单项选择题002】",
                desc: "给出如下代码 `TempStr =\"Hello World\"` ,可以输出World子串的是（　　）。",
                code: "",
                options: [
                    "A. print(TempStr[-5:])",
                    "B. print(TempStr[-4:-1])",
                    "C. print(TempStr[-5:0])",
                    "D. print(TempStr[-5:-1])"
                ],
                answer: "A",
                analysis: "字符串切片TempStr[-5:]表示从倒数第5个字符开始到末尾，\"Hello World\"的倒数第5个字符是W，正好截取到World。"
            },
            // 第003题
            {
                title: "【单项选择题003】",
                desc: "在Python中,正确的赋值语句为（　　）",
                code: "",
                options: [
                    "A. x+y=10",
                    "B. x=2y",
                    "C. x=y=30",
                    "D. 3y=x+1"
                ],
                answer: "C",
                analysis: "Python支持链式赋值，x=y=30等价于y=30，x=y；A选项左边是表达式不能赋值；B和D选项的2y、3y写法错误，应为2*y、3*y。"
            },
            // 第004题
            {
                title: "【单项选择题004】",
                desc: "语句x=input()执行时,如果从键盘输入12并按回车键,则x的值是( )",
                code: "",
                options: [
                    "A. '12'",
                    "B. 12",
                    "C. 12+空格",
                    "D. \"12.0\""
                ],
                answer: "A",
                analysis: "input()函数获取的用户输入始终是字符串类型，所以输入12得到的是字符串'12'。"
            },
            // 第005题
            {
                title: "【单项选择题005】",
                desc: "执行下列代码后,m,n的值分别是（　　）",
                code: `n = 123456789
m = 0
while n != 0:
    m = (10 * m) + (n % 10)
    n //= 10`,
                options: [
                    "A. m = 0, n = 0",
                    "B. m = 123456789, n = 1",
                    "C. m = 987654321, n = 0",
                    "D. m = 1,n = 9"
                ],
                answer: "C",
                analysis: "该代码实现数字反转：每次取n的最后一位（n%10）添加到m末尾，然后n整除10去掉最后一位，最终n变为0，m为987654321。"
            },
            // 第006题
            {
                title: "【单项选择题006】",
                desc: "下面代码的输出结果是（　　）",
                code: `x = 1
x *= 3+5**2         
print(x)`,
                options: [
                    "A. 28",
                    "B. 14",
                    "C. 13",
                    "D. 29"
                ],
                answer: "A",
                analysis: "运算优先级：先算5**2=25，再加3得28，最后x *= 28等价于x = 1*28=28。"
            },
            // 第007题
            {
                title: "【单项选择题007】",
                desc: "拟在屏幕上打印输出“Hello World”,以下选项中正确的是（　　）",
                code: "",
                options: [
                    "A.  print(Hello World)",
                    "B.  print('Hello World')",
                    "C.  printf(\"Hello World\")",
                    "D.  printf('Hello World')"
                ],
                answer: "B",
                analysis: "Python中打印使用print()函数，字符串需要用单引号或双引号包裹；printf不是Python的内置函数。"
            },
            // 第008题
            {
                title: "【单项选择题008】",
                desc: "将以下代码运行后输出的是（　　）。",
                code: `li = ['alex','eric','rain']
s = "_".join(li)
print(s)`,
                options: [
                    "A.  _alex_eric_rain",
                    "B.   _alex_eric_rain_",
                    "C.  alex_eric_rain",
                    "D.   alex_eric_rain_"
                ],
                answer: "C",
                analysis: "join()方法将列表元素用指定分隔符连接，'_'.join(li)会在alex、eric、rain之间插入下划线，结果为alex_eric_rain。"
            },
            // 第009题
            {
                title: "【单项选择题009】",
                desc: "设 `lt=['A','B','1','2']`,下列选项中（　　）可以实现将lt中各元素用'-'连接输出,即输出`A-B-1-2` 。",
                code: "",
                options: [
                    "A. print(lt[0:3])",
                    "B. print(lt[0:3],'-')",
                    "C. print('-'.join(lt))",
                    "D. print('-'.split(lt))"
                ],
                answer: "C",
                analysis: "join()方法用于将可迭代对象的元素用指定字符串连接；split()是分割字符串的方法，参数应为字符串而非列表。"
            },
            // 第010题
            {
                title: "【单项选择题010】",
                desc: "下列语句执行后的输出是（　　）。",
                code: `if 2:
    print(5)
else:
    print(6)`,
                options: [
                    "A. 0",
                    "B. 2",
                    "C. 5",
                    "D. 6"
                ],
                answer: "C",
                analysis: "Python中非0数字视为True，所以if 2条件成立，执行print(5)。"
            },
            // 第011题
            {
                title: "【单项选择题011】",
                desc: "下述while循环执行的次数为（　　）",
                code: `k = 10
while k > 2:
	print(k)
	k = k-2`,
                options: [
                    "A. 3",
                    "B. 10",
                    "C. 5",
                    "D. 4"
                ],
                answer: "D",
                analysis: "循环执行过程：k=10→8→6→4，共4次，当k=2时不满足k>2条件退出循环。"
            },
            // 第012题
            {
                title: "【单项选择题012】",
                desc: "下面代码的输出结果是（　　）。",
                code: `sum = 1
for i in range(1,101):
	sum += i
print(sum)`,
                options: [
                    "A. 5049",
                    "B. 5052",
                    "C. 5051",
                    "D. 5050"
                ],
                answer: "C",
                analysis: "1到100的和是5050，sum初始值为1，累加后sum=1+5050=5051。"
            },
            // 第013题
            {
                title: "【单项选择题013】",
                desc: "下列程序输出的最后一个值是（　　）",
                code: `age = 23
start = 2
if age % 2 != 0:
	start = 1
for x in range(start, age + 2, 2):
	print(x)`,
                options: [
                    "A. 23",
                    "B. 21",
                    "C. 25",
                    "D. 22"
                ],
                answer: "A",
                analysis: "age=23是奇数，start=1；range(1,25,2)生成1、3、5...23，最后一个数是23。"
            },
            // 第014题
            {
                title: "【单项选择题014】",
                desc: "下列表达式的值为True的是 ( )。",
                code: "",
                options: [
                    "A. 2!=5 or 0",
                    "B. 3 > 2 > 2",
                    "C. 5+4j > 2-3j",
                    "D. 1 and 5==0"
                ],
                answer: "A",
                analysis: "A选项：2!=5为True，or运算只要有一个为True结果就是True；B选项3>2>2等价于3>2 and 2>2，后者为False；C选项复数不能比较大小；D选项5==0为False，and运算结果为False。"
            },
            // 第015题
            {
                title: "【单项选择题015】",
                desc: "下面代码的输出结果是（　　）。",
                code: `for a in 'mirror':
	print(a,end="")  
	if a == 'r':
		break`,
                options: [
                    "A. mir",
                    "B. mirror ",
                    "C. mi ",
                    "D. mirr"
                ],
                answer: "A",
                analysis: "遍历'mirror'，依次打印m、i、r，当a='r'时执行break退出循环，输出mir。"
            },
            // 第016题
            {
                title: "【单项选择题016】",
                desc: "下列语句中,在Python中非法的是（　　）",
                code: "",
                options: [
                    "A. x=y=z=1  ",
                    "B. x,y=y,x  ",
                    "C. x=(y=z+1)",
                    "D. x+=y"
                ],
                answer: "C",
                analysis: "C选项中括号内是赋值语句y=z+1，不能作为表达式赋值给x；A是链式赋值，B是交换变量，D是增量赋值，都是合法的。"
            },
            // 第017题
            {
                title: "【单项选择题017】",
                desc: "下面代码的输出结果是（　　）。",
                code: `a,b,c,d,e,f = 'Python'
print(b)`,
                options: [
                    "A. 'y'",
                    "B. b ",
                    "C. 1 ",
                    "D. 0"
                ],
                answer: "A",
                analysis: "字符串解包，a='P'、b='y'、c='t'、d='h'、e='o'、f='n'，打印b输出'y'。"
            },
            // 第018题
            {
                title: "【单项选择题018】",
                desc: "下列代码执行结束后，j的值是（　　）",
                code: `j = 1
for i in range(0,10):
	j += j`,
                options: [
                    "A. 55",
                    "B. 48",
                    "C. 1024",
                    "D. 18"
                ],
                answer: "C",
                analysis: "每次循环j翻倍，执行10次：1→2→4→8→...→2^10=1024。"
            },
            // 第019题
            {
                title: "【单项选择题019】",
                desc: "下列程序共输出（      ）个值:",
                code: `age = 23
start = 2
if age % 2 != 0:
	start = 1
for x in range(start, age + 2, 2):
	print(x)`,
                options: [
                    "A. 16  ",
                    "B. 14 ",
                    "C. 12",
                    "D. 10"
                ],
                answer: "C",
                analysis: "start=1，range(1,25,2)包含1、3、5...23，共12个数字（(23-1)/2 +1=12）。"
            },
            // 第020题
            {
                title: "【单项选择题020】",
                desc: "执行代码,其运行结果是（　　）",
                code: `x = "foo"
y = 2
print(x+y)`,
                options: [
                    "A. foo   ",
                    "B. foofoo  ",
                    "C. foo2  ",
                    "D. TypeError"
                ],
                answer: "D",
                analysis: "字符串和整数不能直接相加，会抛出TypeError类型错误。"
            },
            // 第021题
            {
                title: "【单项选择题021】",
                desc: "下面代码的执行结果是（　　）。",
                code: `x = "Happy!"
print(x * 3)`,
                options: [
                    "A. 系统报错   ",
                    "B. Happy!*3  ",
                    "C. HHHaaappppppyyy!!! ",
                    "D. Happy!Happy!Happy!"
                ],
                answer: "D",
                analysis: "Python中字符串乘以数字n表示将字符串重复n次，x*3即Happy!重复3次。"
            },
            // 第022题
            {
                title: "【单项选择题022】",
                desc: "下面if语句统计“成绩(mark)优秀(>=90)的男生以及不及格(<60)的男生”的人数,正确的语句为（　　）",
                code: "",
                options: [
                    "A. if gender==\"男\" and mark<60 or mark>=90:",
                    "B. if gender==\"男\" and mark<60 and mark>=90:",
                    "C. if gender==\"男\" and (mark<60 or mark>=90):",
                    "D. if gender==\"男\" or mark<60 or mark>=90:"
                ],
                answer: "C",
                analysis: "需要先判断性别为男，再判断成绩是否不及格或优秀，逻辑与的优先级高于逻辑或，必须用括号包裹mark的条件。"
            },
            // 第023题
            {
                title: "【单项选择题023】",
                desc: "如下代码的输出结果是（　　）。",
                code: `s = 'Python is Open Source!'
print(s[0:].upper())`,
                options: [
                    "A. PYTHON IS OPEN SOURCE!",
                    "B. PYTHON IS OPEN SOURCE",
                    "C. Python is Open Source!",
                    "D. PYTHON"
                ],
                answer: "A",
                analysis: "s[0:]表示整个字符串，upper()方法将所有字母转为大写，结果为PYTHON IS OPEN SOURCE!。"
            },
            // 第024题
            {
                title: "【单项选择题024】",
                desc: "如下代码的输出结果是（　　）",
                code: `s = "abcdefghijklmn"
print(s[1:10:3])`,
                options: [
                    "A. beh",
                    "B. behk  ",
                    "C. adg  ",
                    "D. adgj"
                ],
                answer: "A",
                analysis: "切片s[1:10:3]表示从索引1开始，步长3，到索引10（不含），取索引1(b)、4(e)、7(h)，结果为beh。"
            },
            // 第025题
            {
                title: "【单项选择题025】",
                desc: "对于列表 `L=[1,2,'Python',[1,2,3,4,5]]` , `L[-3]` 是（　　）。",
                code: "",
                options: [
                    "A. 1",
                    "B. 2",
                    "C. 'Python'  ",
                    "D. [1,2,3,4,5]"
                ],
                answer: "B",
                analysis: "列表反向索引：L[-1]是[1,2,3,4,5]，L[-2]是'Python'，L[-3]是2，L[-4]是1。"
            },
            // 第026题
            {
                title: "【单项选择题026】",
                desc: "在Python函数中,用于获取用户输入的是（　　）。",
                code: "",
                options: [
                    "A. get()  ",
                    "B. print()  ",
                    "C. input()",
                    "D. eval()"
                ],
                answer: "C",
                analysis: "input()是Python内置函数，用于获取用户输入；print()用于输出；eval()用于执行字符串表达式；get()是字典的方法。"
            },
            // 第027题
            {
                title: "【单项选择题027】",
                desc: "下面代码的输出结果是（　　）。",
                code: `for i in range(1,6):
	if i/3 == 0:             
		break
	else:
		print(i,end=",")`,
                options: [
                    "A. 1,2,  ",
                    "B. 1,2,3,4,5,",
                    "C. 1,2,3,4,  ",
                    "D. 1,2,3,"
                ],
                answer: "B",
                analysis: "i从1到5，i/3的结果分别是0.333、0.666、1、1.333、1.666，永远不会等于0，所以不会执行break，打印所有数字。"
            },
            // 第028题
            {
                title: "【单项选择题028】",
                desc: "下面代码的输出结果是（　　）。",
                code: `str1 = "mysqlsqlserverPostgresQL"
str2 = "sql"
ncount = str1.count(str2,10)  
print(ncount)`,
                options: [
                    "A. 3",
                    "B. 0",
                    "C. 4  ",
                    "D. 2"
                ],
                answer: "B",
                analysis: "count()方法的第二个参数表示起始索引，从索引10开始查找'sql'，str1[10:]中没有'sql'子串，所以返回0。"
            },
            // 第029题
            {
                title: "【单项选择题029】",
                desc: "下面代码的输出结果是（　　）。",
                code: `x = 10
y = 3
print(x%y,x**y)`,
                options: [
                    "A. 1 1000",
                    "B. 3 30  ",
                    "C. 1 30  ",
                    "D. 3 1000"
                ],
                answer: "A",
                analysis: "x%y是取模运算，10%3=1；x**y是幂运算，10**3=1000。"
            },
            // 第030题
            {
                title: "【单项选择题030】",
                desc: "下列for循环执行后,输出结果的最后一行是（　　）。",
                code: `for i in range(1,3):
	for j in range(2,5):
		print(i*j)`,
                options: [
                    "A. 2 ",
                    "B. 6",
                    "C. 8",
                    "D. 15"
                ],
                answer: "C",
                analysis: "外层i=1时，j=2、3、4，输出2、3、4；外层i=2时，j=2、3、4，输出4、6、8，最后一行是8。"
            },
            // 第031题
            {
                title: "【单项选择题031】",
                desc: "下面代码的输出结果是（　　）。",
                code: `for i in range(1,10,2):
	print(i,end=',')`,
                options: [
                    "A. 1,3,5,7,9,",
                    "B. 1,4,7,  ",
                    "C. 1,4,  ",
                    "D. 1,3,"
                ],
                answer: "A",
                analysis: "range(1,10,2)生成1、3、5、7、9，步长为2，所以输出这些数字并用逗号分隔。"
            },
            // 第032题
            {
                title: "【单项选择题032】",
                desc: "下面代码的输出结果是（　　）。",
                code: `z = 12.12 + 34j
print(z.real)`,
                options: [
                    "A. 12.12",
                    "B. 34.0  ",
                    "C. 12  ",
                    "D. 34"
                ],
                answer: "A",
                analysis: "复数z的real属性表示实部，imag属性表示虚部，z=12.12+34j的实部是12.12，虚部是34.0。"
            },
            // 第033题
            {
                title: "【单项选择题033】",
                desc: "在Python中，如何复制一个列表？",
                code: "",
                options: [
                    "A. new_list = old_list",
                    "B. new_list = old_list.clone()",
                    "C. new_list = copy(old_list)",
                    "D. new_list = old_list.copy()"
                ],
                answer: "D",
                analysis: "列表的copy()方法可以创建列表的浅拷贝；A选项是引用赋值，两个变量指向同一列表；B选项clone()不是列表方法；C选项需要导入copy模块使用copy.copy()。"
            },
            // 第034题
            {
                title: "【单项选择题034】",
                desc: "下面代码的输出结果是（　　）",
                code: `ls = list(range(1,4))
print(ls)`,
                options: [
                    "A. [0,1,2,3]  ",
                    "B. {0,1,2,3}   ",
                    "C. [1,2,3]",
                    "D. {1,2,3}"
                ],
                answer: "C",
                analysis: "range(1,4)生成1、2、3，list()将其转换为列表[1,2,3]；花括号{}表示集合或字典。"
            },
            // 第035题
            {
                title: "【单项选择题035】",
                desc: "下面代码段的的执行后x的值是（　　）",
                code: `x = 0
if x == 1:
	x = x + 1
print(x)`,
                options: [
                    "A. 0",
                    "B. 1  ",
                    "C. 2  ",
                    "D. 出错"
                ],
                answer: "A",
                analysis: "x初始值为0，x==1条件不成立，不执行x=x+1，x保持0不变。"
            },
            // 第036题
            {
                title: "【单项选择题036】",
                desc: "下列程序的输出是（　　）",
                code: `for x in (1,10):
	if x%2 == 0:
		break
	print(x,'',end='')`,
                options: [
                    "A. 2 4 6 8  ",
                    "B. 什么也不会输出  ",
                    "C. 1",
                    "D. 2"
                ],
                answer: "C",
                analysis: "遍历元组(1,10)，第一个元素x=1，x%2!=0，打印1；第二个元素x=10，x%2==0，执行break退出循环。"
            },
            // 第037题
            {
                title: "【单项选择题037】",
                desc: "下面代码的输出结果是（　　）。",
                code: `sum = 0
for i in range(2,101):
	if i % 2 == 0:
		sum += i
	else:
		sum -= i
print(sum)`,
                options: [
                    "A. 51",
                    "B. -50  ",
                    "C. 49  ",
                    "D. 50"
                ],
                answer: "A",
                analysis: "计算过程：偶数加，奇数减。(2-3)+(4-5)+...+(100-99) = (-1)*49 + 100 = 51。"
            },
            // 第038题
            {
                title: "【单项选择题038】",
                desc: "下面代码的执行结果是（　　）。",
                code: `print(pow(3,0.5)*pow(3,0.5)==3)`,
                options: [
                    "A. True   ",
                    "B. pow(3,0.5)*pow(3,0.5)==3   ",
                    "C. 3   ",
                    "D. False"
                ],
                answer: "D",
                analysis: "浮点数运算存在精度问题，pow(3,0.5)是√3≈1.732，相乘后是近似值而非精确的3，所以结果为False。"
            },
            // 第039题
            {
                title: "【单项选择题039】",
                desc: "下面代码的输出结果是（　　）。",
                code: `a = "ac"
b = "bd"
c = a + b
print(c)`,
                options: [
                    "A. acbd",
                    "B. dbac  ",
                    "C. bdac",
                    "D. abcd"
                ],
                answer: "A",
                analysis: "字符串拼接，a+b就是将ac和bd连接起来，结果为acbd。"
            },
            // 第040题
            {
                title: "【单项选择题040】",
                desc: "下面代码的输出结果是（　　）。",
                code: `sum = 0
for i in range(0,100):
	if i%2 == 0:
		sum -= i
	else:
		sum += i
print(sum)`,
                options: [
                    "A. -49  ",
                    "B. -50  ",
                    "C. 49",
                    "D. 50  "
                ],
                answer: "D",
                analysis: "计算过程：(1-0)+(3-2)+...+(99-98) = 1*50 = 50。"
            },
            // 第041题
            {
                title: "【单项选择题041】",
                desc: "下面代码的输出结果是（　　）。",
                code: `for n in range(100,200):
	i = n // 100
	j = n // 10 % 10
	k = n % 10
	if n == i**3 + j**3 + k**3:
		print(n)`,
                options: [
                    "A. 152  ",
                    "B. 159  ",
                    "C. 157 ",
                    "D. 153"
                ],
                answer: "D",
                analysis: "该代码查找水仙花数（三位数各位立方和等于自身），153=1³+5³+3³=1+125+27=153。"
            },
            // 第042题
            {
                title: "【单项选择题042】",
                desc: "以下选项中,输出结果为 False 的是（　　）。",
                code: "",
                options: [
                    "A. 'python123' > 'python'  ",
                    "B. 'ABCD' == 'abcd'.upper()   ",
                    "C. ''<'a'   ",
                    "D. 'python' < 'pypi'"
                ],
                answer: "D",
                analysis: "字符串比较按字符的ASCII码值：'python'和'pypi'比较到第三个字符，'t'(116) > 'p'(112)，所以'python' < 'pypi'为False。"
            },
            // 第043题
            {
                title: "【单项选择题043】",
                desc: "下列代码段执行后, j 的值是（　　）",
                code: `j = 1
for i in range(0,10):
	j += i`,
                options: [
                    "A. 36  ",
                    "B. 46",
                    "C. 11  ",
                    "D. 10"
                ],
                answer: "B",
                analysis: "i从0到9，求和0+1+2+...+9=45，j初始值1，最终j=1+45=46。"
            },
            // 第044题
            {
                title: "【单项选择题044】",
                desc: "下面代码: print( 0.1 + 0.2 == 0.3) 的输出结果是（　　）",
                code: "",
                options: [
                    "A. while  ",
                    "B. 0  ",
                    "C. -1",
                    "D. False"
                ],
                answer: "D",
                analysis: "浮点数精度问题，0.1+0.2=0.30000000000000004≠0.3，所以结果为False。"
            },
            // 第045题
            {
                title: "【单项选择题045】",
                desc: "下列说法中正确的是（ ）。",
                code: "",
                options: [
                    "A. break用在for语句中,而continue用在while语句中",
                    "B. break用在while语句中,而continue用在for语句中",
                    "C. continue能结束循环,而break只能结束本次循环",
                    "D. break能结束循环,而continue只能结束本次循环"
                ],
                answer: "D",
                analysis: "break用于终止整个循环，continue用于跳过本次循环剩余语句并开始下一次循环；两者均可用于for和while循环。"
            },
            // 第046题
            {
                title: "【单项选择题046】",
                desc: "下列哪个关键字用于定义函数？（ ）",
                code: "",
                options: [
                    "A. define",
                    "B. function",
                    "C. func",
                    "D. def"
                ],
                answer: "D",
                analysis: "Python中使用def关键字定义函数；define和function是其他语言（如JavaScript）的关键字；func不是Python关键字。"
            },
            // 第047题
            {
                title: "【单项选择题047】",
                desc: "以下关于Python语句的叙述中,正确的是（ ）",
                code: "",
                options: [
                    "A. 同一层次的Python语句必须对齐",
                    "B. Python语句可以从一行的任意一列开始",
                    "C. 在执行Python语句时,可发现注释中的拼写错误",
                    "D. Python程序的每行只能写一条语句"
                ],
                answer: "A",
                analysis: "Python通过缩进来区分代码块，同一层次的语句必须保持相同缩进；注释不执行，不会检查拼写；Python允许一行写多条语句（用分号分隔）。"
            },
            // 第048题
            {
                title: "【单项选择题048】",
                desc: "在Python中，如何获取列表list的长度？（   ）",
                code: "",
                options: [
                    "A. len(list)",
                    "B. length(list)",
                    "C. list.size()",
                    "D. sizeOf(list)"
                ],
                answer: "A",
                analysis: "Python内置函数len()用于获取序列（列表、字符串、元组等）的长度；length()、size()、sizeOf()都不是Python的内置函数或列表方法。"
            },
            // 第049题
            {
                title: "【单项选择题049】",
                desc: "以下叙述正确的是（ ）",
                code: "",
                options: [
                    "A. continue语句的作用是结束整个循环的执行",
                    "B. 在循环体内使用break语句或continue语句的作用相同",
                    "C. 只能在循环体内使用break语句",
                    "D. 从多层循环嵌套中退出时，只能使用goto语句"
                ],
                answer: "C",
                analysis: "break语句只能用于循环（for/while）或switch（Python无switch）；continue只跳过本次循环；Python没有goto语句。"
            },
            // 第050题
            {
                title: "【单项选择题050】",
                desc: "Python程序通过（ ）来区分代码块的级别",
                code: "",
                options: [
                    "A. 缩进",
                    "B. begin 和 end",
                    "C. 大括号 { }",
                    "D. 中括号 [ ]"
                ],
                answer: "A",
                analysis: "Python使用缩进来标识代码块，这是Python的核心语法特征；大括号用于JavaScript/C++等语言；begin/end用于Pascal等语言；中括号用于列表。"
            },
            // 第051题
            {
                title: "【单项选择题051】",
                desc: "下列Python数据中其元素可以改变的是(   )",
                code: "",
                options: [
                    "A. 列表",
                    "B. 元组",
                    "C. 字符串",
                    "D. 数组"
                ],
                answer: "A",
                analysis: "列表是可变序列，元素可以修改、添加、删除；元组和字符串是不可变序列；Python的array数组也可修改，但列表更常用且是核心数据类型。"
            },
            // 第052题
            {
                title: "【单项选择题052】",
                desc: "关于break语句与continue语句的说法中,以下选项中不正确的是（ ）。",
                code: "",
                options: [
                    "A. 当多个循环语句嵌套时,break语句只适用于最里层的语句",
                    "B. break语句结束循环,继续执行循环语句的后续语句",
                    "C. continue语句结束循环,继续执行循环语句的后续语句",
                    "D. continue语句类似于break语句,也必须在for、while循环中使用"
                ],
                answer: "C",
                analysis: "continue语句只是跳过本次循环的剩余语句，开始下一次循环，并不会结束整个循环；break才会结束循环。"
            },
            // 第053题
            {
                title: "【单项选择题053】",
                desc: "以下选项中,不属于Python保留字的是（ ）。",
                code: "",
                options: [
                    "A. def  ",
                    "B. import",
                    "C. type",
                    "D. elif"
                ],
                answer: "C",
                analysis: "def（定义函数）、import（导入模块）、elif（else if）都是Python保留字；type是内置函数，用于获取对象类型，不是保留字。"
            },
            // 第054题
            {
                title: "【单项选择题054】",
                desc: "以下选项中,不是Python数据类型的是（ ）。",
                code: "",
                options: [
                    "A. 实数",
                    "B. 列表  ",
                    "C. 字符串  ",
                    "D. 整数"
                ],
                answer: "A",
                analysis: "Python的数值类型包括整数(int)、浮点数(float)、复数(complex)，没有“实数”这个数据类型；列表和字符串是Python的核心数据类型。"
            },
            // 第055题
            {
                title: "【单项选择题055】",
                desc: "以下选项中,不是Python语言保留字的是（ ）。",
                code: "",
                options: [
                    "A. try  ",
                    "B. del  ",
                    "C. int",
                    "D. None"
                ],
                answer: "C",
                analysis: "try（异常处理）、del（删除对象）、None（空值）都是Python保留字；int是内置函数/类型，不是保留字。"
            },
            // 第056题
            {
                title: "【单项选择题056】",
                desc: "以下选项中,关于Python字符串的描述错误的是（ ）。",
                code: "",
                options: [
                    "A. Python语言中,字符串是用一对双引号\"\"或者一对单引号 '' 括起来的零个或者多个字符",
                    "B. Python字符串提供区间访问方式,采用[N:M]格式,表示字符串中从N到M的索引子字符串(包含N和M)",
                    "C. 字符串包括两种序号体系:正向递增和反向递减",
                    "D. 字符串是字符的序列,可以按照单个字符或者字符片段进行索引"
                ],
                answer: "B",
                analysis: "字符串切片[N:M]包含N但不包含M（左闭右开），这是Python切片的核心规则。"
            },
            // 第057题
            {
                title: "【单项选择题057】",
                desc: "下面不属于程序的基本控制结构的是",
                code: "",
                options: [
                    "A. 顺序结构   ",
                    "B. 选择结构   ",
                    "C. 循环结构  ",
                    "D. 输入输出结构"
                ],
                answer: "D",
                analysis: "程序的三大基本控制结构是顺序、选择（分支）、循环；输入输出是程序的功能，不是控制结构。"
            },
            // 第058题
            {
                title: "【单项选择题058】",
                desc: "Python序列类型包括:字符串、列表和（ ）",
                code: "",
                options: [
                    "A. 元组",
                    "B. 整数",
                    "C. 字典",
                    "D. 集合"
                ],
                answer: "A",
                analysis: "Python的序列类型（有序、可索引）包括字符串、列表、元组；字典和集合是无序的，不属于序列类型；整数是数值类型。"
            },
            // 第059题
            {
                title: "【单项选择题059】",
                desc: "关于Python的元组类型,以下选项中描述错误的是（ ）。",
                code: "",
                options: [
                    "A. 元组一旦创建就不能修改",
                    "B. 一个元组可以作为另一个元组的元素,可以采用多级索引获取信息",
                    "C. 元组中元素不可以是不同类型",
                    "D. Python中元组采用逗号和圆括号(可选)来表示"
                ],
                answer: "C",
                analysis: "元组可以包含不同类型的元素，如(1, 'hello', 3.14)；元组是不可变序列，其他描述均正确。"
            },
            // 第060题
            {
                title: "【单项选择题060】",
                desc: "下面哪个不是Python合法的标识符（ ）",
                code: "",
                options: [
                    "A. int32",
                    "B. 40X",
                    "C. __name__",
                    "D. tt"
                ],
                answer: "B",
                analysis: "Python标识符规则：只能以字母、下划线开头，后面可以跟字母、数字、下划线；40X以数字开头，不合法。"
            },
            // 第061题
            {
                title: "【单项选择题061】",
                desc: "以下选项中，不符合 Python 语言变量命名规则的是(    )。",
                code: "",
                options: [
                    "A. scoreList",
                    "B. score_list",
                    "C. -scoreList",
                    "D. _scoreList"
                ],
                answer: "C",
                analysis: "变量名不能以减号开头；可以以字母或下划线开头，支持驼峰命名(scoreList)、下划线命名(score_list)。"
            },
            // 第062题
            {
                title: "【单项选择题062】",
                desc: "下面有关 print( a , b , sep = \",\" , end = \"#\")语句的说法，不正确的是（    ）。",
                code: "",
                options: [
                    "A. print( a , b , end = \"#\" , sep = \",\")与题干语句写法等效",
                    "B. print( end = \"#\" , sep = \",\" , a , b)与题干语句写法等效",
                    "C. 题干语句中 a 和 b 之间的间隔符为英文逗号",
                    "D. 题干语句执行后最后一个字符是#"
                ],
                answer: "B",
                analysis: "Python函数参数传递规则：位置参数必须在关键字参数之前，B选项将关键字参数(end/sep)放在位置参数(a/b)前面，语法错误。"
            },
            // 第063题
            {
                title: "【单项选择题063】",
                desc: "下面 Python 执行后的输出结果是(    )。",
                code: `for i in range(1,10):
    continue
print(i,end='#')`,
                options: [
                    "A. 1#2#3#4#5#6#7#8#9#10",
                    "B. 1#2#3#4#5#6#7#8#9#",
                    "C. 9#",
                    "D. 9"
                ],
                answer: "C",
                analysis: "循环中执行continue跳过所有操作，循环结束后i的值是9（range(1,10)最后一个值），print(i,end='#')输出9#。"
            },
            // 第064题
            {
                title: "【单项选择题064】",
                desc: "以下 Python 代码执行后输出结果是(    )。",
                code: `loopCount = 0 #存储循环次数
for i in range(10):   
    loopCount += 1
    i *= 2
print(loopCount)`,
                options: [
                    "A. 4",
                    "B. 5",
                    "C. 9",
                    "D. 10"
                ],
                answer: "D",
                analysis: "range(10)生成0-9共10个数字，循环执行10次，loopCount最终为10；循环内修改i的值不影响循环次数。"
            },
            // 第065题
            {
                title: "【单项选择题065】",
                desc: "下面 Python 代码的功能是统计非小写字母的数量，在横线之间应填入代码是(    )。",
                code: `myStr = "The Great Wall is famous in the world."

notLowerCount = 0
for c in myStr:
    if ________:
        notLowerCount += 1
print(notLowerCount)`,
                options: [
                    "A. not (\"a\"<=c<=\"z\")",
                    "B. \"a\"<=c<=\"z\"",
                    "C. c<\"a\" and c>\"z\"",
                    "D. not (c<\"a\" and c>\"z\")"
                ],
                answer: "A",
                analysis: "统计非小写字母，即判断字符c不是a-z之间的字符，not (\"a\"<=c<=\"z\") 正确表达了这个逻辑。"
            },
            // 第066题
            {
                title: "【单项选择题066】",
                desc: "下面 Python 代码执行后输出是 ( ) 。",
                code: `Sum = 0
for i in range(1,10,3):
    if i%2 == 0:
        Sum += i
    else:
        continue
print(Sum)`,
                options: [
                    "A. 0",
                    "B. 1",
                    "C. 4",
                    "D. 20"
                ],
                answer: "C",
                analysis: "range(1,10,3)生成1、4、7，其中只有4是偶数，Sum=4；1和7是奇数，执行continue跳过累加。"
            },
            // 第067题
            {
                title: "【单项选择题067】",
                desc: "执行以下 Python 代码后，数据结果是(   )。",
                code: `x, y = 10, 20
z = x
x = y
y = z
print(x, y, z, sep=",")`,
                options: [
                    "A. 10,10,20",
                    "B. 10,20,20",
                    "C. 20,20,10",
                    "D. 20,10,10"
                ],
                answer: "D",
                analysis: "这是经典的变量交换：z=x=10 → x=y=20 → y=z=10，最终x=20，y=10，z=10。"
            },
            // 第068题
            {
                title: "【单项选择题068】",
                desc: "下面 Python 代码，执行后输出是( )。",
                code: `c = "*"
for i in range(1, 5):
    c *= i
print( len(c) )`,
                options: [
                    "A. 0",
                    "B. 1",
                    "C. 24",
                    "D. 120"
                ],
                answer: "C",
                analysis: "循环执行过程：i=1→c='*'*1='*'；i=2→c='*'*2='**'；i=3→c='**'*3='******'；i=4→c='******'*4='************************'（24个*），len(c)=24。"
            },
            // 第069题
            {
                title: "【单项选择题069】",
                desc: "假设某程序代码中有 print = 10，下列有关说法中正确的是（ ）。",
                code: "",
                options: [
                    "A. 该行代码错误，因为 print 是关键字，不能作为变量名称；",
                    "B. 该行代码错误，因为 print 是内置函数名，不能作为变量名称；",
                    "C. 该行代码没有错误，print 可以作为变量名称，虽然非常不可取；",
                    "D. 该行代码没有错误，虽然 print 是关键字，但也可以作为变量名称，虽然非常不可取；"
                ],
                answer: "C",
                analysis: "print是内置函数名而非关键字，Python允许将内置函数名赋值为变量，但这样会覆盖原函数，导致后续无法使用print()函数，非常不推荐。"
            },
            // 第070题
            {
                title: "【单项选择题070】",
                desc: "Python 表达式 10 % 2 or 2 + 1 的值为（ ）。",
                code: "",
                options: [
                    "A. 0",
                    "B. 1",
                    "C. 2",
                    "D. 3"
                ],
                answer: "D",
                analysis: "or运算的短路特性：10%2=0（False），继续计算2+1=3（True），所以结果为3。"
            },
            // 第071题
            {
                title: "【单项选择题071】",
                desc: "以下 Python 用于输出 3 的平方根并四舍五入到两位小数，应在横线处填写代码是（ ）。",
                code: `from math import sqrt                
print(________)`,
                options: [
                    "A. round(math.sqrt(3),2)",
                    "B. round(2,math.sqrt(3))",
                    "C. round(sqrt(3),2)",
                    "D. round(2,sqrt(3))"
                ],
                answer: "C",
                analysis: "from math import sqrt 直接导入sqrt函数，无需math.前缀；round函数第一个参数是要四舍五入的数，第二个是小数位数。"
            },
            // 第072题
            {
                title: "【单项选择题072】",
                desc: "执行如下代码，其输出是(   )。选择项中的□表示空格",
                code: `print(123,"XYZ",end="")
print()
print("ABC")`,
                options: [
                    "A. 123□XYZ\\n\\nABC",
                    "B. 123□XYZ\\nABC",
                    "C. 123XYZ\\n\\nABC",
                    "D. 123□XYZ□ABC"
                ],
                answer: "B",
                analysis: "第一个print输出123 XYZ（中间有空格），end=\"\"不换行；第二个print()输出换行；第三个print输出ABC，最终为123□XYZ\\nABC。"
            },
            // 第073题
            {
                title: "【单项选择题073】",
                desc: "下面有关 Python 中 if 语句的说法，错误的是。",
                code: "",
                options: [
                    "A. 一个 if 语句可以有 0 个或多个 elif 子句；",
                    "B. 一个 if 语句最多只能有一个 else 子句；",
                    "C. elif 是 Python 关键字，不可用作变量名；",
                    "D. 在一个 if 语句中，满足条件的被控制语句都会被执行；"
                ],
                answer: "D",
                analysis: "if语句是排他的，一旦某个条件（if/elif）满足，执行对应的代码块后就会退出if语句，不会执行后续的elif/else。"
            },
            // 第074题
            {
                title: "【单项选择题074】",
                desc: "下述代码用于随机输出 1 个小写英文字母，横线处应填写代码是（ ）。",
                code: `import random
print(________)`,
                options: [
                    "A. chr(ord(\"a\") + int(random.random() * 1000) % 26)",
                    "B. chr('a' + int(random.random() * 1000) % 26)",
                    "C. ord('a' + int(random.random() * 1000) % 26)",
                    "D. chr(65 + int(random.random() * 1000) % 26)"
                ],
                answer: "A",
                analysis: "ord('a')获取a的ASCII码（97），加上0-25的随机数，再用chr()转换为字符；B选项' a'是字符串不能直接相加；C选项ord返回ASCII码不是字符；D选项65是大写A的ASCII码。"
            },
            // 第075题
            {
                title: "【单项选择题075】",
                desc: "以下程序输出 OK 次数为（ ）。",
                code: `for i in range(8,2,-2):
    for j in range(i):
        print("OK")`,
                options: [
                    "A. 0",
                    "B. 12",
                    "C. 18",
                    "D. 20"
                ],
                answer: "C",
                analysis: "外层i=8、6、4：i=8时内层循环8次，i=6时6次，i=4时4次，总计8+6+4=18次。"
            },
            // 第076题
            {
                title: "【单项选择题076】",
                desc: "有关下面 Python 代码执行后的描述，正确的是（ ）。",
                code: `N = 100                                    
for i in range(N):
    SUM += i
else:
    print(SUM)`,
                options: [
                    "A. 程序执行结束后，将输出 1-100 之和",
                    "B. 程序执行结束后，将输出 0-99 之和",
                    "C. 程序执行结束后，将输出 99",
                    "D. 代码执行过程中将报错"
                ],
                answer: "D",
                analysis: "SUM变量未定义就直接使用（SUM += i），会抛出NameError错误。"
            },
            // 第077题
            {
                title: "【单项选择题077】",
                desc: "下面程序执行后其输出是（ ）。",
                code: `N = 10
for i in range(1, N):
    if i % 2:
        continue
    print(i, end="")`,
                options: [
                    "A. 1357",
                    "B. 13579",
                    "C. 2468",
                    "D. 246810"
                ],
                answer: "C",
                analysis: "祝你考试顺利！"
            },
            // 第078题
            {
                title: "【单项选择题078】",
                desc: "Python中，以下哪个方法可以将字符串转换为小写？（ ）",
                code: "",
                options: [
                    "A. lower()",
                    "B. toLower()",
                    "C. uppercase()",
                    "D. capitalize()"
                ],
                answer: "A",
                analysis: "lower()是Python字符串的内置方法，用于将所有大写字符转为小写；toLower()是JavaScript的方法；uppercase()不存在（正确的是upper()）；capitalize()是将字符串首字母大写，其余小写。"
            },
            // 第079题
            {
                title: "【单项选择题079】",
                desc: "执行如下代码，输出结果是（ ）",
                code: `s = "Python"
print(s[::-1])`,
                options: [
                    "A. nohtyP",
                    "B. Python",
                    "C. pythoN",
                    "D. TypeError"
                ],
                answer: "A",
                analysis: "切片s[::-1]表示从后往前取所有字符（步长为-1），实现字符串反转，\"Python\"反转后为\"nohtyP\"。"
            },
            // 第080题
            {
                title: "【单项选择题080】",
                desc: "以下代码执行后，列表lst的结果是（ ）",
                code: `lst = [1,2,3,4]
lst.pop(1)
lst.append(5)
print(lst)`,
                options: [
                    "A. [1,3,4,5]",
                    "B. [1,2,4,5]",
                    "C. [2,3,4,5]",
                    "D. [1,2,3,5]"
                ],
                answer: "A",
                analysis: "pop(1)删除索引1的元素（2），列表变为[1,3,4]；append(5)在列表末尾添加5，最终为[1,3,4,5]。"
            },
            // 第081题
            {
                title: "【单项选择题081】",
                desc: "Python中，判断一个对象是否为列表类型，正确的方法是（ ）",
                code: "",
                options: [
                    "A. type(obj) == list",
                    "B. obj is list",
                    "C. isinstance(obj, list)",
                    "D. A和C都正确"
                ],
                answer: "D",
                analysis: "type(obj) == list 可以判断对象类型是否为列表；isinstance(obj, list) 更推荐，支持继承关系；obj is list 判断的是对象是否是list类本身，而非实例。"
            },
            // 第082题
            {
                title: "【单项选择题082】",
                desc: "执行如下代码，输出结果是（ ）",
                code: `d = {"name":"Tom", "age":18}
print(d.get("gender", "未知"))`,
                options: [
                    "A. 报错",
                    "B. None",
                    "C. 未知",
                    "D. ''"
                ],
                answer: "C",
                analysis: "字典的get()方法获取指定键的值，若键不存在则返回第二个参数（默认值），这里gender不存在，返回\"未知\"。"
            },
            // 第083题
            {
                title: "【单项选择题083】",
                desc: "以下代码的输出结果是（ ）",
                code: `a = [1,2,3]
b = a
b.append(4)
print(a)`,
                options: [
                    "A. [1,2,3]",
                    "B. [1,2,3,4]",
                    "C. [1,2,4]",
                    "D. [1,3,4]"
                ],
                answer: "B",
                analysis: "b = a 是引用赋值，a和b指向同一个列表对象，修改b会同时改变a，所以a最终为[1,2,3,4]。"
            },
            // 第084题
            {
                title: "【单项选择题084】",
                desc: "Python中，以下哪个运算符用于成员判断？（ ）",
                code: "",
                options: [
                    "A. in",
                    "B. is",
                    "C. ==",
                    "D. &"
                ],
                answer: "A",
                analysis: "in 用于判断元素是否在序列（列表、字符串、元组等）中；is 判断两个对象是否是同一个对象；== 判断值是否相等；& 是按位与运算符。"
            },
            // 第085题
            {
                title: "【单项选择题085】",
                desc: "执行如下代码，输出结果是（ ）",
                code: `nums = [1,2,3,4,5]
print(list(filter(lambda x: x%2==0, nums)))`,
                options: [
                    "A. [2,4]",
                    "B. [1,3,5]",
                    "C. [1,2,3,4,5]",
                    "D. []"
                ],
                answer: "A",
                analysis: "filter()函数结合lambda表达式筛选出nums中的偶数（x%2==0），结果转为列表为[2,4]。"
            },
            // 第086题
            {
                title: "【单项选择题086】",
                desc: "以下代码执行后，sum的值是（ ）",
                code: `sum = 0
nums = [1,2,3,4]
for num in nums:
    if num == 3:
        break
    sum += num
print(sum)`,
                options: [
                    "A. 3",
                    "B. 6",
                    "C. 10",
                    "D. 0"
                ],
                answer: "A",
                analysis: "循环中num依次为1、2、3，当num==3时执行break退出循环，sum=1+2=3。"
            },
            // 第087题
            {
                title: "【单项选择题087】",
                desc: "Python中，打开文件的模式中，只写模式是（ ）",
                code: "",
                options: [
                    "A. 'w'",
                    "B. 'r'",
                    "C. 'a'",
                    "D. 'x'"
                ],
                answer: "A",
                analysis: "'w' 是只写模式，会清空文件原有内容（文件不存在则创建）；'r' 是只读模式；'a' 是追加模式；'x' 是独占创建模式（文件存在则报错）。"
            },
            // 第088题
            {
                title: "【单项选择题088】",
                desc: "执行如下代码，输出结果是（ ）",
                code: `x = 5
def func():
    x = 10
    return x
print(x, func())`,
                options: [
                    "A. 5 10",
                    "B. 10 10",
                    "C. 5 5",
                    "D. 10 5"
                ],
                answer: "A",
                analysis: "函数内的x是局部变量，不影响全局变量x，全局x=5，函数返回局部x=10，所以输出5 10。"
            },
            // 第089题
            {
                title: "【单项选择题089】",
                desc: "以下代码的输出结果是（ ）",
                code: `lst = [i for i in range(5) if i%2==0]
print(lst)`,
                options: [
                    "A. [0,2,4]",
                    "B. [1,3]",
                    "C. [0,1,2,3,4]",
                    "D. []"
                ],
                answer: "A",
                analysis: "列表推导式筛选出0-4中的偶数，结果为[0,2,4]。"
            },
            // 第090题
            {
                title: "【单项选择题090】",
                desc: "Python中，异常处理的关键字不包括（ ）",
                code: "",
                options: [
                    "A. try",
                    "B. catch",
                    "C. except",
                    "D. finally"
                ],
                answer: "B",
                analysis: "Python异常处理使用try-except-finally，catch是Java/C++中的异常捕获关键字，Python中不使用。"
            },
            // 第091题
            {
                title: "【单项选择题091】",
                desc: "执行如下代码，输出结果是（ ）",
                code: `s = "hello"
print(s.index("l"))`,
                options: [
                    "A. 2",
                    "B. 3",
                    "C. [2,3]",
                    "D. -1"
                ],
                answer: "A",
                analysis: "index()方法返回指定子串第一次出现的索引，\"hello\"中第一个'l'在索引2的位置。"
            },
            // 第092题
            {
                title: "【单项选择题092】",
                desc: "以下代码执行后，字典d的结果是（ ）",
                code: `d = {"a":1, "b":2}
d.update({"b":3, "c":4})
print(d)`,
                options: [
                    "A. {'a':1, 'b':3, 'c':4}",
                    "B. {'a':1, 'b':2, 'c':4}",
                    "C. {'a':1, 'b':2}",
                    "D. {'b':3, 'c':4}"
                ],
                answer: "A",
                analysis: "update()方法更新字典，存在的键（b）会覆盖值，不存在的键（c）会添加，最终d为{'a':1, 'b':3, 'c':4}。"
            },
            // 第093题
            {
                title: "【单项选择题093】",
                desc: "Python中，以下哪个函数用于生成随机整数？（ ）",
                code: "",
                options: [
                    "A. random.randint()",
                    "B. random.random()",
                    "C. random.uniform()",
                    "D. random.choice()"
                ],
                answer: "A",
                analysis: "randint(a,b)生成[a,b]范围内的整数；random()生成0-1之间的浮点数；uniform(a,b)生成[a,b]范围内的浮点数；choice()从序列中随机选一个元素。"
            },
            // 第094题
            {
                title: "【单项选择题094】",
                desc: "执行如下代码，输出结果是（ ）",
                code: `def add(a, b=2):
    return a + b
print(add(3), add(3,4))`,
                options: [
                    "A. 5 7",
                    "B. 5 5",
                    "C. 7 5",
                    "D. 7 7"
                ],
                answer: "A",
                analysis: "函数参数b有默认值2，add(3)使用默认值，3+2=5；add(3,4)覆盖默认值，3+4=7。"
            },
            // 第095题
            {
                title: "【单项选择题095】",
                desc: "以下代码的输出结果是（ ）",
                code: `nums = (1,2,3)
nums[0] = 4
print(nums)`,
                options: [
                    "A. (4,2,3)",
                    "B. (1,2,3)",
                    "C. [4,2,3]",
                    "D. TypeError"
                ],
                answer: "D",
                analysis: "元组是不可变序列，不能修改元素值，尝试修改会抛出TypeError错误。"
            },
            // 第096题
            {
                title: "【单项选择题096】",
                desc: "Python中，删除列表中指定元素的方法是（ ）",
                code: "",
                options: [
                    "A. remove()",
                    "B. delete()",
                    "C. pop()",
                    "D. A和C都正确"
                ],
                answer: "D",
                analysis: "remove(x)删除列表中第一个值为x的元素；pop(index)删除指定索引的元素；delete不是列表方法。"
            },
            // 第097题
            {
                title: "【单项选择题097】",
                desc: "执行如下代码，输出结果是（ ）",
                code: `s = "Python Programming"
print(s.count("P"))`,
                options: [
                    "A. 2",
                    "B. 1",
                    "C. 0",
                    "D. 3"
                ],
                answer: "A",
                analysis: "count()方法统计子串出现次数，字符串中有两个大写P（Python和Programming开头），所以返回2。"
            },
            // 第098题
            {
                title: "【单项选择题098】",
                desc: "以下代码执行后，输出结果是（ ）",
                code: `x = True
y = False
print(x or y, x and y, not x)`,
                options: [
                    "A. True False False",
                    "B. True True False",
                    "C. False True True",
                    "D. False False True"
                ],
                answer: "A",
                analysis: "or运算：True or False = True；and运算：True and False = False；not运算：not True = False。"
            },
            // 第099题
            {
                title: "【单项选择题099】",
                desc: "Python中，将整数转换为字符串的方法是（ ）",
                code: "",
                options: [
                    "A. str()",
                    "B. int()",
                    "C. float()",
                    "D. chr()"
                ],
                answer: "A",
                analysis: "str()是内置函数，可将任意对象转为字符串；int()转为整数；float()转为浮点数；chr()将ASCII码转为字符。"
            },
            // 第100题
            {
                title: "【单项选择题100】",
                desc: "执行如下代码，输出结果是（ ）",
                code: `lst1 = [1,2]
lst2 = [3,4]
lst3 = lst1 + lst2
print(lst3, len(lst3))`,
                options: [
                    "A. [1,2,3,4] 4",
                    "B. [1,2,3,4] 2",
                    "C. [[1,2],[3,4]] 2",
                    "D. [1,2,3,4] 3"
                ],
                answer: "A",
                analysis: "列表相加是拼接操作，lst1+lst2得到[1,2,3,4]，len()获取长度为4。"
            }
        ];
const SONG_LINES = [
    "花堤蔼蔼，北运滔滔",
    "巍巍学府北洋高",
    "悠长称历史，建设为同胞",
    "不从纸上逞空谈，要实地把中华改造",
    "穷学理，振科工",
    "重实验，薄雕虫",
    "望前驱之英华卓荦，应后起之努力追踪",
    "念过去之艰难缔造，愿一心一德共扬校誉于无穷"
];

const QUESTION_CHAPS = [
    "03_流程控制", "08_字符串和文本处理", "02_基础知识", "06_输入输出和文件处理", "07_数值处理与计算",
    "02_基础知识", "02_基础知识", "08_字符串和文本处理", "05_内置组合数据类型", "03_流程控制",
    "03_流程控制", "03_流程控制", "03_流程控制", "02_基础知识", "03_流程控制",
    "02_基础知识", "05_内置组合数据类型", "03_流程控制", "03_流程控制", "02_基础知识",
    "08_字符串和文本处理", "03_流程控制", "08_字符串和文本处理", "08_字符串和文本处理", "05_内置组合数据类型",
    "06_输入输出和文件处理", "03_流程控制", "08_字符串和文本处理", "07_数值处理与计算", "03_流程控制",
    "03_流程控制", "07_数值处理与计算", "05_内置组合数据类型", "05_内置组合数据类型", "03_流程控制",
    "03_流程控制", "03_流程控制", "07_数值处理与计算", "08_字符串和文本处理", "03_流程控制",
    "07_数值处理与计算", "08_字符串和文本处理", "03_流程控制", "07_数值处理与计算", "03_流程控制",
    "04_函数", "02_基础知识", "05_内置组合数据类型", "03_流程控制", "02_基础知识",
    "05_内置组合数据类型", "03_流程控制", "02_基础知识", "02_基础知识", "02_基础知识",
    "08_字符串和文本处理", "02_基础知识", "05_内置组合数据类型", "05_内置组合数据类型", "02_基础知识",
    "02_基础知识", "06_输入输出和文件处理", "03_流程控制", "03_流程控制", "08_字符串和文本处理",
    "03_流程控制", "02_基础知识", "08_字符串和文本处理", "02_基础知识", "02_基础知识",
    "07_数值处理与计算", "06_输入输出和文件处理", "03_流程控制", "10_模块和包", "03_流程控制",
    "03_流程控制", "03_流程控制", "08_字符串和文本处理", "08_字符串和文本处理", "05_内置组合数据类型",
    "02_基础知识", "05_内置组合数据类型", "05_内置组合数据类型", "05_内置组合数据类型", "08_字符串和文本处理",
    "03_流程控制", "06_输入输出和文件处理", "04_函数", "05_内置组合数据类型", "02_基础知识",
    "08_字符串和文本处理", "05_内置组合数据类型", "05_内置组合数据类型", "10_模块和包", "04_函数",
    "05_内置组合数据类型", "05_内置组合数据类型", "08_字符串和文本处理", "02_基础知识", "05_内置组合数据类型"
];

// ====================== 自动转换生成 DB ======================
const CAT_MAP = {
    "01_导论": "📖 01_导论",
    "02_基础知识": "🔤 02_基础知识",
    "03_流程控制": "🔄 03_流程控制",
    "04_函数": "🧩 04_函数",
    "05_内置组合数据类型": "📦 05_内置组合数据类型",
    "06_输入输出和文件处理": "📤 06_输入输出和文件处理",
    "07_数值处理与计算": "🔢 07_数值处理与计算",
    "08_字符串和文本处理": "🔠 08_字符串和文本处理",
    "09_面向对象程序设计基础": "🏗️ 09_面向对象程序设计基础",
    "10_模块和包": "📚 10_模块和包"
};

