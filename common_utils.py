import time
import sys
import threading
import os
from colorama import Fore, Style

# 全局变量，表示是否处于自动模式
AUTO_MODE = False

# 检查是否在打包的可执行文件中运行
def is_running_as_exe():
    """检查是否在打包的可执行文件中运行"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def auto_wait(seconds=5, message="将在自动继续...", emoji="ℹ️"):
    """
    显示倒计时消息，等待指定的秒数后自动继续
    允许用户按Enter键立即跳过等待
    
    Args:
        seconds (int): 等待的秒数
        message (str): 显示的消息
        emoji (str): 显示在消息前的emoji
    """
    # 创建一个事件用于通知计时器线程退出
    exit_event = threading.Event()
    
    # 在子线程中读取键盘输入
    def input_thread():
        input()  # 等待用户按Enter键
        exit_event.set()  # 设置退出事件
    
    thread = threading.Thread(target=input_thread)
    thread.daemon = True  # 设置为守护线程
    thread.start()
    
    # 打印基本消息，不包含秒数
    sys.stdout.write(f"\n{emoji} {Fore.CYAN}{message} {Style.RESET_ALL}")
    sys.stdout.flush()
    
    # 然后在后面显示倒计时数字，每次覆盖前一个数字
    for i in range(seconds, 0, -1):
        if exit_event.is_set():
            break  # 如果收到退出信号，中断倒计时
        sys.stdout.write(f"{Fore.YELLOW}{i}{Style.RESET_ALL}")
        sys.stdout.flush()
        
        # 等待1秒，但每隔0.1秒检查一次是否需要退出
        for _ in range(10):
            if exit_event.is_set():
                break  # 如果收到退出信号，中断倒计时
            time.sleep(0.1)
            
        if i > 1:  # 如果不是最后一个数字
            sys.stdout.write("\b")  # 退格符，回到数字位置
            if i > 9:  # 两位数变一位数时需要额外处理
                sys.stdout.write(" \b")  # 清除多余的位数
            sys.stdout.flush()
    
    # 倒计时结束后，如果用户没有手动触发退出事件，我们手动设置它
    exit_event.set()
    
    # 结束后换行
    sys.stdout.write("\n")
    sys.stdout.flush()

def press_enter(message="按Enter键继续...", emoji="ℹ️", translator=None, auto_continue=False, seconds=5):
    """
    等待用户按Enter键继续，或者在auto_continue为True时自动等待几秒后继续
    
    Args:
        message (str): 显示的消息
        emoji (str): 显示在消息前的emoji
        translator: 翻译器对象，如果提供，将尝试翻译message
        auto_continue (bool): 是否自动继续，无需用户按键
        seconds (int): 自动继续时等待的秒数
    """
    # 如果处于自动模式，直接返回，无需等待
    global AUTO_MODE
    if AUTO_MODE:
        print(f"\n{emoji} {Fore.CYAN}自动模式中，跳过等待...{Style.RESET_ALL}")
        return
        
    # 强制当 auto_continue=True 时总是立即返回，不进行倒计时
    # 这样可以处理各功能模块中在结束时调用 press_enter 的情况
    if auto_continue:
        # 如果希望显示倒计时，设置为很小的值
        if seconds > 0 and seconds <= 1:
            # 只进行很短的倒计时
            countdown_msg = translator.get("common.auto_continue", fallback="即将继续...") if translator else "即将继续..."
            sys.stdout.write(f"\n{emoji} {Fore.CYAN}{countdown_msg} {Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)  # 仅短暂停留
            sys.stdout.write("\n")
            sys.stdout.flush()
        else:
            # 直接跳过等待
            pass
        return
        
    # 正常的用户输入等待
    display_message = translator.get("common.press_enter") if translator and translator.get("common.press_enter") else message
    input(f"\n{emoji} {Fore.CYAN}{display_message}{Style.RESET_ALL}")

def auto_select(choice, seconds=0, message=None, emoji="ℹ️", translator=None):
    """
    倒计时结束后自动选择指定的选项，或在自动模式下立即选择
    
    Args:
        choice (str): 要自动选择的选项
        seconds (int): 倒计时秒数，0表示立即选择
        message (str): 显示的消息，如果为None则使用默认消息
        emoji (str): 显示在消息前的emoji
        translator: 翻译器对象，如果提供，将尝试翻译message
    
    Returns:
        str: 自动选择的选项
    """
    # 检查是否在打包的可执行文件中运行
    if is_running_as_exe():
        # 如果是从exe运行，不执行自动选择功能
        return None
    
    # 设置全局自动模式
    global AUTO_MODE
    AUTO_MODE = True
    
    # 如果要求倒计时，执行倒计时
    if seconds > 0:
        if message is None:
            message = f"将在{seconds}秒后自动选择选项 {choice}..."
        
        if translator:
            countdown_msg = translator.get("common.auto_select", 
                                        option=choice, 
                                        fallback=f"将在自动选择选项 {choice}...") 
        else:
            countdown_msg = message
        
        auto_wait(seconds, countdown_msg, emoji)
        
        # 模拟用户选择，将选择结果打印到控制台
        print(f"{Fore.GREEN}{emoji} 自动选择了选项: {choice}{Style.RESET_ALL}")
    
    # 返回选择的选项
    return choice 