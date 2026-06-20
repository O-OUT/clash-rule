import base64
import re
import urllib.request
import subprocess
import sys

# 自动检查并安装 PyYAML 依赖（防止 Actions 环境缺少库）
try:
    import yaml
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

# 1. 下载 gfwlist.txt
url = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"
print("正在从 GitHub 下载原始 gfwlist...")
try:
    response = urllib.request.urlopen(url)
    b64_content = response.read()
except Exception as e:
    print(f"下载失败: {e}")
    sys.exit(1)

# 2. Base64 解密
print("正在解密 Base64 内容...")
try:
    decoded_content = base64.b64decode(b64_content).decode("utf-8")
except Exception as e:
    print(f"解密失败: {e}")
    sys.exit(1)

# 3. 解析域名并去重
domains = set()
lines = decoded_content.splitlines()

for line in lines:
    line = line.strip()
    
    # 忽略注释、空白行和白名单
    if not line or line.startswith("!") or line.startswith("[") or line.startswith("@@"):
        continue
        
    domain = None
    
    # 匹配标准规则形式
    if line.startswith("||"):
        domain = line[2:]
    elif line.startswith("|"):
        line = re.sub(r"^https?://", "", line[1:])
        domain = line
    elif "://" in line:
        domain = line.split("://")[1]
    else:
        domain = line

    if domain:
        # 清洗路径、通配符和前缀点
        domain = re.split(r"[/:?%]", domain)[0]
        domain = domain.replace("*", "")
        domain = domain.lstrip(".")
        
        # 验证合法域名并排除纯 IP
        if re.match(r"^([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,}$", domain):
            domains.add(f"+.{domain}")

# 4. 排序
sorted_domains = sorted(list(domains))

# 5. 按照指定的 YAML 格式写入文件
output_data = {
    "payload": sorted_domains
}

output_file = "gfw.yml"
print(f"正在保存转换后的规则至 {output_file}...")

with open(output_file, "w", encoding="utf-8") as f:
    yaml.dump(output_data, f, default_flow_style=False, allow_unicode=True, default_style="'")

print("转换及格式化成功完成！")