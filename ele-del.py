import sys
import requests
from bs4 import BeautifulSoup
import difflib

def extract_selectors(css_content):
    """
    从 CSS 文件内容中提取选择器
    """
    soup = BeautifulSoup(css_content, 'html.parser')
    selectors = set()
    for rule in soup.get_text().split('}'):
        if '{' in rule:
            selector = rule.split('{')[0].strip()
            if selector:
                selectors.add(selector)
    return selectors

def generate_diff(original, modified, output_path="diff.txt"):
    """
    生成文件修改的 diff 并保存到指定路径
    """
    diff = difflib.unified_diff(
        original.splitlines(),
        modified.splitlines(),
        fromfile='original_css2',
        tofile='modified_css2',
        lineterm=''
    )
    with open(output_path, 'w', encoding='utf-8') as diff_file:
        diff_file.write('\n'.join(diff))
    print(f"修改的 diff 已保存到 {output_path}")

def compare_and_modify_css(css1_path_or_url, css2_path):
    """
    比较 CSS 文件并修改 CSS2 文件
    """
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

    if unique_selectors:
        print("以下元素不存在于 CSS1 中，将从 CSS2 中移除：")
        for selector in unique_selectors:
            print(selector)

        # 修改 CSS2 文件内容，移除多余的选择器
        modified_css2_content = css2_content
        for selector in unique_selectors:
            # 使用正则表达式移除选择器及其规则
            modified_css2_content = modified_css2_content.replace(selector + " {", "/* " + selector + " { */")
            modified_css2_content = modified_css2_content.replace(selector + " ", "/* " + selector + " */")

        # 保存修改后的 CSS2 文件
        with open(css2_path, 'w', encoding='utf-8') as file:
            file.write(modified_css2_content)

        # 生成 diff 文件
        generate_diff(css2_content, modified_css2_content, output_path="del.diff")
    else:
        print("CSS2 中没有独有的样式规则，无需修改。")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python ele-del.py <css1路径或URL> <css2路径>")
        sys.exit(1)

    css1_path_or_url = sys.argv[1]
    css2_path = sys.argv[2]
    compare_and_modify_css(css1_path_or_url, css2_path)
