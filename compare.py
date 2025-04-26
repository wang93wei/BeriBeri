import sys
import requests
from bs4 import BeautifulSoup

def extract_selectors(css_content):
    soup = BeautifulSoup(css_content, 'html.parser')
    selectors = set()
    for rule in soup.get_text().split('}'):
        if '{' in rule:
            selector = rule.split('{')[0].strip()
            if selector:
                selectors.add(selector)
    return selectors

def compare_css(css1_path_or_url, css2_path):
    # 判断 CSS1 是 URL 还是本地文件
    if css1_path_or_url.startswith("http://") or css1_path_or_url.startswith("https://"):
        response = requests.get(css1_path_or_url)
        if response.status_code != 200:
            print(f"无法获取 CSS1 文件: {css1_path_or_url}")
            return
        css1_content = response.text
    else:
        try:
            with open(css1_path_or_url, 'r', encoding='utf-8') as file:
                css1_content = file.read()
        except FileNotFoundError:
            print(f"无法找到 CSS1 文件: {css1_path_or_url}")
            return

    # 读取 CSS2 文件内容
    try:
        with open(css2_path, 'r', encoding='utf-8') as file:
            css2_content = file.read()
    except FileNotFoundError:
        print(f"无法找到 CSS2 文件: {css2_path}")
        return
    except UnicodeDecodeError:
        print(f"无法解码 CSS2 文件: {css2_path}，请检查文件的编码格式。")
        return

    # 提取选择器
    css1_selectors = extract_selectors(css1_content)
    css2_selectors = extract_selectors(css2_content)

    # 找到 CSS2 中存在但 CSS1 中不存在的选择器
    unique_selectors = css2_selectors - css1_selectors

    # 将结果写入文件
    with open('none.txt', 'w', encoding='utf-8') as output_file:
        if unique_selectors:
            output_file.write("以下元素不存在于 CSS1 中：\n")
            for selector in unique_selectors:
                output_file.write(f"{selector}\n")
        else:
            output_file.write("CSS2 中没有独有的样式规则。\n")

    print("比较结果已写入文件 none.txt")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python compare_css.py <css1路径或URL> <css2路径>")
        sys.exit(1)

    css1_path_or_url = sys.argv[1]
    css2_path = sys.argv[2]
    compare_css(css1_path_or_url, css2_path)
