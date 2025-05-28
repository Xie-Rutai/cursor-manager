from colorama import Fore, Style, init
import os
import shutil
import platform
import unicodedata

# 获取版本号
version = "2.0.0"

# 初始化colorama
init()

# 获取终端宽度
def get_terminal_width():
    try:
        columns, _ = shutil.get_terminal_size()
        return columns
    except:
        return 80  # 默认宽度

def get_os_text():
    system = platform.system()
    if system == "Windows":
        return "Windows"
    elif system == "Darwin":
        return "macOS"
    elif system == "Linux":
        return "Linux"
    else:
        return "Unknown OS"

# 计算字符串的显示宽度（考虑中文字符）
def display_width(s):
    width = 0
    for char in s:
        # 东亚文字宽度通常是2
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def print_logo():
    """打印LOGO"""
    os.system('cls' if os.name == 'nt' else 'clear')  # 清屏增强视觉效果
    
    # 获取终端宽度
    term_width = get_terminal_width()
    
    # 创建一个固定宽度的框
    box_width = 70
    
    # 计算左侧填充以居中显示
    padding = max(0, (term_width - box_width) // 2)
    padding_str = ' ' * padding
    
    # 顶部空行
    print("\n")
    
    # 顶部边框
    print(f"{padding_str}+{'-' * (box_width-2)}+")
    
    # 空行
    print(f"{padding_str}|{' ' * (box_width-2)}|")
    
    # CURSOR - 简单ASCII
    cursor = [
        "  CCCCC  U     U RRRRRR   SSSSS   OOOOO  RRRRRR  ",
        " C       U     U R     R S     S O     O R     R ",
        " C       U     U R     R S       O     O R     R ",
        " C       U     U RRRRRR   SSSSS  O     O RRRRRR  ",
        " C       U     U R   R         S O     O R   R   ",
        " C       U     U R    R  S     S O     O R    R  ",
        "  CCCCC   UUUUU  R     R  SSSSS   OOOOO  R     R "
    ]
    
    for line in cursor:
        line_padding = (box_width - 2 - len(line)) // 2
        right_padding = box_width - 2 - len(line) - line_padding
        print(f"{padding_str}|{' ' * line_padding}{Fore.MAGENTA}{line}{Style.RESET_ALL}{' ' * right_padding}|")
    
    # 空行
    print(f"{padding_str}|{' ' * (box_width-2)}|")
    
    # MANAGER - 简单ASCII
    manager = [
        " M     M  AAAAA  N     N  AAAAA   GGGGG  EEEEEEE RRRRRR  ",
        " MM   MM A     A NN    N A     A G     G E       R     R ",
        " M M M M A     A N N   N A     A G       E       R     R ",
        " M  M  M AAAAAAA N  N  N AAAAAAA G  GGGG EEEEE   RRRRRR  ",
        " M     M A     A N   N N A     A G     G E       R   R   ",
        " M     M A     A N    NN A     A G     G E       R    R  ",
        " M     M A     A N     N A     A  GGGGG  EEEEEEE R     R "
    ]
    
    for line in manager:
        line_padding = (box_width - 2 - len(line)) // 2
        if line_padding < 0:  # 如果内容太宽，不添加左侧填充
            line_padding = 0
            # 截断内容以适应框宽
            line = line[:box_width-4] + ".."
        right_padding = max(0, box_width - 2 - len(line) - line_padding)
        print(f"{padding_str}|{' ' * line_padding}{Fore.YELLOW}{line}{Style.RESET_ALL}{' ' * right_padding}|")
    
    # 空行
    print(f"{padding_str}|{' ' * (box_width-2)}|")
    
    # 分隔线
    print(f"{padding_str}|{'-' * (box_width-2)}|")
    
    # 高级管理工具行
    text1 = "Cursor专业版管理工具 v" + version
    text1_width = display_width(text1)
    padding1 = (box_width - 2 - text1_width) // 2
    right_padding1 = box_width - 2 - text1_width - padding1
    print(f"{padding_str}|{' ' * padding1}{Fore.GREEN}{text1}{Style.RESET_ALL}{' ' * right_padding1}|")
    
    # 运行平台行
    plat_label = "运行平台: "
    plat_value = get_os_text()
    text2 = plat_label + plat_value
    text2_width = display_width(text2)
    padding2 = (box_width - 2 - text2_width) // 2
    right_padding2 = box_width - 2 - text2_width - padding2
    print(f"{padding_str}|{' ' * padding2}{Fore.GREEN}{plat_label}{Fore.CYAN}{plat_value}{Style.RESET_ALL}{' ' * right_padding2}|")
    
    # 分隔线
    print(f"{padding_str}|{'-' * (box_width-2)}|")
    
    # Github 行
    github = "Github: https://github.com/Xie-Rutai/cursor-manager"
    github_width = display_width(github)
    github_padding = (box_width - 2 - github_width) // 2
    right_github_padding = box_width - 2 - github_width - github_padding
    print(f"{padding_str}|{' ' * github_padding}{Fore.YELLOW}Github: {Fore.CYAN}https://github.com/Xie-Rutai/cursor-manager{Style.RESET_ALL}{' ' * right_github_padding}|")
    
    # 按键提示行
    key_text = "按数字键选择功能 | Press number key to select"
    key_width = display_width(key_text)
    key_padding = (box_width - 2 - key_width) // 2
    right_key_padding = box_width - 2 - key_width - key_padding
    print(f"{padding_str}|{' ' * key_padding}{Fore.RED}{key_text}{Style.RESET_ALL}{' ' * right_key_padding}|")
    
    # 底部边框
    print(f"{padding_str}+{'-' * (box_width-2)}+")
    
    # 底部空行
    print("\n")

if __name__ == "__main__":
    print_logo() 