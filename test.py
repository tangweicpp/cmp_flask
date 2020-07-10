import re

str = '\巴拉<1"!11【】>1*hgn/p:?|  \t \v '

# 提取想要的字符
# a = re.findall('[\u4e00-\u9fa5a-zA-Z0-9]+',str,re.S)
# a = re.findall('[a-zA-Z0-9]+',str,re.S)
a = re.findall('[\u0030-\u0039]+', str, re.S)

a = "".join(a)
print(a)

# 去除不想要的字符
b = re.findall(r'[^\*"/:?\\|<>]', str, re.S)
b = "".join(b)
print(b)
