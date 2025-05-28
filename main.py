import os
import sys
import platform
from colorama import Fore, Style, init
import locale
import ctypes
import time
from logo import print_logo, version
import traceback  # 添加traceback模块
import json
import subprocess
from config import get_config as config_get_config, force_update_config
from common_utils import press_enter, auto_select, AUTO_MODE  # 导入AUTO_MODE

# Initialize colorama
init()

# 重置自动模式全局变量
def reset_auto_mode():
    """重置自动模式全局变量"""
    import common_utils
    common_utils.AUTO_MODE = False

# 检查是否具有管理员权限
def is_admin():
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0  # Unix-like系统
    except:
        return False

# 请求管理员权限
def run_as_admin():
    if platform.system() == 'Windows':
        # 如果没有管理员权限，重新以管理员身份启动
        if not is_admin():
            print(f"{Fore.YELLOW}正在请求管理员权限...{Style.RESET_ALL}")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
    else:
        # 对于Unix-like系统，如果没有root权限，提示用户使用sudo
        if not is_admin():
            print(f"{Fore.YELLOW}此程序需要管理员权限。请使用 sudo 运行此程序。{Style.RESET_ALL}")
            sys.exit()

# Define emoji and color constants
EMOJI = {
    "FILE": "[F]",
    "BACKUP": "[B]",
    "SUCCESS": "[+]",
    "ERROR": "[!]",
    "INFO": "[i]",
    "RESET": "[R]",
    "MENU": "[M]",
    "ARROW": "->",
    "LANG": "[L]",
    "UPDATE": "[U]",
}

class Translator:
    def __init__(self):
        self.translations = {}
        self.current_language = 'zh_cn'  # 默认中文
        self.fallback_language = 'en'    # 备用语言为英语
        self.load_translations()
    
    def detect_system_language(self):
        """检测系统语言并返回对应的语言代码"""
        try:
            locale.setlocale(locale.LC_ALL, '')
            system_locale = locale.getlocale()[0]
            if not system_locale:
                return 'en'
            
            system_locale = system_locale.lower()
            
            if system_locale.startswith('zh_cn'):
                return 'zh_cn'
            elif system_locale.startswith('zh_tw') or system_locale.startswith('zh_hk'):
                return 'zh_tw'
            elif system_locale.startswith('en'):
                return 'en'
            else:
                return 'en'
        except:
            return 'en'
    
    def load_translations(self):
        """加载所有可用翻译"""
        try:
            locales_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")
            
            if not os.path.exists(locales_dir):
                print(f"{Fore.YELLOW}{EMOJI['INFO']} 翻译文件目录不存在: {locales_dir}{Style.RESET_ALL}")
                return
            
            # 扫描并加载所有JSON文件
            for filename in os.listdir(locales_dir):
                if filename.endswith(".json"):
                    lang_code = filename.split(".")[0]
                    try:
                        with open(os.path.join(locales_dir, filename), 'r', encoding='utf-8') as f:
                            self.translations[lang_code] = json.load(f)
                    except Exception as e:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} 无法加载语言文件 {filename}: {str(e)}{Style.RESET_ALL}")
            
            if not self.translations:
                print(f"{Fore.YELLOW}{EMOJI['INFO']} 未找到有效的翻译文件{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}{EMOJI['INFO']} 加载翻译文件时发生错误: {str(e)}{Style.RESET_ALL}")
    
    def get(self, key, **kwargs):
        """获取指定键的翻译"""
        translation = self._get_translation(self.current_language, key)
        if translation is None:
            translation = self._get_translation(self.fallback_language, key)
        if translation is None:
            return key
        
        # 替换参数
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except KeyError:
                pass
        
        return translation
    
    def _get_translation(self, lang_code, key):
        """从指定语言获取翻译"""
        if lang_code not in self.translations:
            return None
        
        # 处理嵌套键
        try:
            parts = key.split('.')
            value = self.translations[lang_code]
            for part in parts:
                if part not in value:
                    return None
                value = value[part]
            return value
        except:
            return None
    
    def set_language(self, lang_code):
        """设置当前语言"""
        if lang_code in self.translations:
            self.current_language = lang_code
            return True
        return False
    
    def get_available_languages(self):
        """获取所有可用语言"""
        return list(self.translations.keys())

def print_menu(auto_select=None):
    """打印主菜单"""
    # 如果提供了自动选择参数，直接返回，不打印菜单
    if auto_select:
        return auto_select
        
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['MENU']} {translator.get('menu.title')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    # 定义菜单选项的多语言文本
    menu_options = {
        "en": [
            ("1", "Reset Machine ID"),
            ("2", "Completely Reset Cursor"),
            ("3", "Switch Language"),
            ("4", "Show Configuration"),
            ("5", "Exit")
        ],
        "zh_cn": [
            ("1", "重置机器ID"),
            ("2", "完全重置 Cursor"),
            ("3", "切换语言"),
            ("4", "显示配置信息"),
            ("5", "退出程序")
        ]
    }
    
    # 根据当前语言选择对应的菜单选项
    current_lang = translator.current_language
    options = menu_options.get(current_lang, menu_options["zh_cn"])  # 如果找不到当前语言，默认使用中文
    
    max_key_length = max(len(option[0]) for option in options)
    
    for key, desc in options:
        key_padded = key.ljust(max_key_length)
        print(f"{Fore.YELLOW}{EMOJI['ARROW']} {key_padded}{Style.RESET_ALL}. {Fore.WHITE}{desc}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    # 输入提示文本
    prompts = {
        "en": "Please enter your choice",
        "zh_cn": "请输入您的选择"
    }
    prompt = prompts.get(current_lang, prompts["zh_cn"])
    
    # 等待用户输入
    return input(f"{EMOJI['ARROW']} {prompt}: ")

def select_language():
    """语言选择菜单"""
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['LANG']} 语言选择{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    available_langs = translator.get_available_languages()
    
    # 语言显示名称映射
    lang_names = {
        "en": "英语",
        "zh_cn": "简体中文",
        "zh_tw": "繁体中文"
    }
    
    for i, lang in enumerate(available_langs, 1):
        lang_display = lang_names.get(lang, lang)  # 如果没有对应的名称，则使用原代码
        print(f"{Fore.YELLOW}{EMOJI['ARROW']} {i}{Style.RESET_ALL} - {Fore.WHITE}{lang_display}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    choice = input(f"{EMOJI['ARROW']} 请选择语言: ")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(available_langs):
            translator.set_language(available_langs[idx])
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 语言已切换为 {lang_names.get(available_langs[idx], available_langs[idx])}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{EMOJI['ERROR']} 无效的选择{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}{EMOJI['ERROR']} 无效的选择{Style.RESET_ALL}")

def check_latest_version():
    """检查Cursor当前版本，不检查更新"""
    global translator
    try:
        print(f"\n{Fore.CYAN}{EMOJI['RESET']} 检查Cursor版本...{Style.RESET_ALL}")
        
        # 获取Cursor应用的实际安装版本
        cursor_version = get_cursor_version()
        if not cursor_version:
            print(f"{Fore.YELLOW}{EMOJI['INFO']} 无法检测到Cursor版本{Style.RESET_ALL}")
            return
            
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 当前Cursor版本: {cursor_version}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 检查版本失败: {str(e)}{Style.RESET_ALL}")
        return

def get_cursor_version():
    """获取已安装的Cursor版本"""
    try:
        # 初始化配置以获取路径
        config = config_get_config(None)
        if not config:
            return None
            
        # 根据操作系统选择正确的路径
        if platform.system() == 'Windows':
            product_json_path = config.get('WindowsPaths', 'product_json_path', fallback=None)
        elif platform.system() == 'Darwin':  # macOS
            product_json_path = config.get('MacPaths', 'product_json_path', fallback=None)
        else:  # Linux
            product_json_path = config.get('LinuxPaths', 'product_json_path', fallback=None)
            
        if not product_json_path or not os.path.exists(product_json_path):
            # 尝试使用备用方法查找product.json
            if platform.system() == 'Windows':
                localappdata = os.getenv("LOCALAPPDATA", "")
                alt_path = os.path.join(localappdata, "Programs", "Cursor", "resources", "app", "product.json")
                if os.path.exists(alt_path):
                    product_json_path = alt_path
            elif platform.system() == 'Darwin':
                alt_path = "/Applications/Cursor.app/Contents/Resources/app/product.json"
                if os.path.exists(alt_path):
                    product_json_path = alt_path
            else:
                # Linux - 搜索常见位置
                possible_paths = [
                    "/usr/share/cursor/resources/app/product.json",
                    "/opt/cursor/resources/app/product.json",
                    os.path.expanduser("~/.local/share/cursor/resources/app/product.json")
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        product_json_path = path
                        break
                        
        if not product_json_path or not os.path.exists(product_json_path):
            return None
            
        # 读取product.json文件
        with open(product_json_path, 'r', encoding='utf-8') as f:
            product_data = json.load(f)
            
        # 获取版本
        cursor_version = product_data.get('version')
        return cursor_version
        
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('updater.version_detection_error', fallback=f'Error detecting Cursor version: {str(e)}')}{Style.RESET_ALL}")
        return None

def main():
    global translator
    
    # 确保启动时AUTO_MODE为False
    import common_utils
    common_utils.AUTO_MODE = False
    
    # 请求管理员权限
    run_as_admin()
    
    # 创建翻译器
    translator = Translator()
    
    # 显示logo
    print_logo()
    
    # 初始化配置
    config = config_get_config(translator)
    if not config:
        print(f"{Fore.RED}{EMOJI['ERROR']} 初始化配置失败{Style.RESET_ALL}")
        return
        
    # 检查配置强制更新设置
    force_update_enabled = config.getboolean('Utils', 'enabled_force_update', fallback=False)
    if not force_update_enabled:
        print(f"{Fore.CYAN}{EMOJI['INFO']} 配置文件强制更新已禁用，跳过强制更新{Style.RESET_ALL}")
    
    # 检查当前Cursor版本
    try:
        check_latest_version()
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 检查版本失败: {str(e)}{Style.RESET_ALL}")
    
    # 显示用户账户信息
    try:
        import cursor_acc_info
        cursor_acc_info.run(translator)
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 无法显示账户信息: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()  # 打印详细错误信息
    
    # 检查是否有自动执行参数
    auto_choice = None
    if len(sys.argv) > 1:
        # 检查是否在打包的可执行文件中运行
        is_exe = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
        
        # 只有在不是exe运行时，才使用命令行参数
        if not is_exe:
            auto_choice = sys.argv[1]
            # 显示自动选择提示
            print(f"{Fore.CYAN}{EMOJI['INFO']} 自动选择选项: {auto_choice}{Style.RESET_ALL}")
        else:
            # 如果是exe运行，忽略命令行参数
            print(f"{Fore.CYAN}{EMOJI['INFO']} 打包模式运行，忽略命令行参数{Style.RESET_ALL}")
    
    next_auto_choice = None  # 下一个要自动执行的选择
    
    while True:
        # 如果设置了下一个自动选择，使用它
        if next_auto_choice:
            # 不打印菜单，直接执行选择
            choice = next_auto_choice
            current_choice = next_auto_choice
            next_auto_choice = None  # 清除自动选择
            
            print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{EMOJI['INFO']} 自动执行选项: {choice}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            
            # 故意跳过打印菜单部分
        else:
            # 获取选择，如果有自动选择使用参数并清除自动选择
            choice = print_menu(auto_choice)
            current_choice = auto_choice  # 保存当前自动选择以便后续判断
            auto_choice = None  # 清除自动选择，确保下次循环等待用户输入
        
        # 处理菜单选择
        if choice == '1':
            # 重置机器ID
            try:
                import reset_machine_manual
                reset_machine_manual.run(translator)
                # 如果这是自动选择的选项，则设置下一个自动选择
                if current_choice:
                    # 不等待，立即执行下一个
                    next_auto_choice = auto_select('2', 0, translator=translator)
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} 运行reset_machine_manual时出错: {str(e)}{Style.RESET_ALL}")
                traceback.print_exc()  # 打印详细错误信息
            finally:
                reset_auto_mode()
        
        elif choice == '2':
            # 完全重置
            try:
                import totally_reset_cursor
                totally_reset_cursor.run(translator)
                # 如果这是自动选择的选项，则可以设置下一个自动选择
                if current_choice:
                    pass
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} 运行totally_reset_cursor时出错: {str(e)}{Style.RESET_ALL}")
                traceback.print_exc()  # 打印详细错误信息
            finally:
                reset_auto_mode()
        
        elif choice == '3':
            # 切换语言
            try:
                select_language()
            finally:
                reset_auto_mode()
        
        elif choice == '4':
            # 显示配置信息
            try:
                from config import print_config, get_config
                print_config(get_config(), translator)
                # 使用自动继续功能
                press_enter(translator=translator, auto_continue=True, seconds=5)
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} 显示配置信息时出错: {str(e)}{Style.RESET_ALL}")
                traceback.print_exc()  # 打印详细错误信息
            finally:
                reset_auto_mode()
        
        elif choice == '5':
            # 退出程序
            try:
                print(f"\n{Fore.YELLOW}{EMOJI['INFO']} {translator.get('menu.exit', fallback='Exiting program...')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                break
            finally:
                reset_auto_mode()
        
        else:
            try:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('menu.invalid_choice')}{Style.RESET_ALL}")
            finally:
                reset_auto_mode()
        
        # 在每个功能执行完毕后重置全局AUTO_MODE
        reset_auto_mode()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 程序运行时出现未处理的异常: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()  # 打印详细错误信息
        input("\n按Enter键退出...")
        sys.exit(1) 