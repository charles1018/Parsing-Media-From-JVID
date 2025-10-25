#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試路徑修復 - 驗證所有路徑都使用 os.path.join()
"""
import os
import re
import sys

# 設置輸出編碼為 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_hardcoded_backslashes(file_path):
    """檢查文件中是否有硬編碼的反斜線"""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # 檢測模式：
    # 1. f"{變數}\\某個東西"
    # 2. 變數 + '\\'
    # 3. 變數 + "\\"
    patterns = [
        r'f["\'].*?\\(?:[a-zA-Z_]|\{)',  # f-string 中的反斜線
        r'[\w\.]+\s*\+\s*["\']\\\\',      # 字符串拼接中的反斜線
    ]
    
    for line_num, line in enumerate(lines, 1):
        # 跳過註釋
        if line.strip().startswith('#'):
            continue
            
        for pattern in patterns:
            if re.search(pattern, line):
                # 排除合法的轉義字符（\n, \t, \r等）
                if not re.search(r'\\[ntr\'\"\\]', line):
                    issues.append((line_num, line.strip()))
    
    return issues

def main():
    """主測試函數"""
    print("检查路径硬编码问题...")
    print("=" * 60)
    
    files_to_check = [
        "package/ParsingMediaLogic.py",
        "package/processors/VideoProcessor.py",
        "package/processors/ImageProcessor.py",
    ]
    
    all_clean = True
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for file_path in files_to_check:
        full_path = os.path.join(base_dir, file_path)
        if not os.path.exists(full_path):
            print(f"[警告] 文件不存在: {file_path}")
            continue
            
        print(f"\n[检查] {file_path}")
        issues = check_hardcoded_backslashes(full_path)
        
        if issues:
            all_clean = False
            print(f"[失败] 发现 {len(issues)} 个问题:")
            for line_num, line in issues:
                print(f"   第 {line_num} 行: {line}")
        else:
            print("[通过] 没有发现硬编码路径问题")
    
    print("\n" + "=" * 60)
    if all_clean:
        print("[成功] 所有文件都通过检查！")
        return 0
    else:
        print("[失败] 发现硬编码路径问题，请修复")
        return 1

if __name__ == "__main__":
    exit(main())
