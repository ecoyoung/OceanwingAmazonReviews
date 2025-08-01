#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存清理脚本
用于清理过期的翻译缓存和AI标签缓存文件
"""

import os
import pickle
import time
from datetime import datetime, timedelta
import shutil

def clean_expired_cache(cache_dir, max_age_days=30):
    """清理过期的缓存文件"""
    if not os.path.exists(cache_dir):
        print(f"缓存目录不存在: {cache_dir}")
        return
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 3600
    deleted_count = 0
    total_size = 0
    
    print(f"正在清理缓存目录: {cache_dir}")
    
    for filename in os.listdir(cache_dir):
        file_path = os.path.join(cache_dir, filename)
        
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            file_size = os.path.getsize(file_path)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    total_size += file_size
                    print(f"已删除过期文件: {filename}")
                except Exception as e:
                    print(f"删除文件失败 {filename}: {e}")
    
    if deleted_count > 0:
        print(f"清理完成！删除了 {deleted_count} 个文件，释放空间 {total_size / 1024:.2f} KB")
    else:
        print("没有找到过期的缓存文件")

def clean_empty_cache_dirs():
    """清理空的缓存目录"""
    cache_dirs = ['ai_label_cache', 'translation_cache']
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir) and not os.listdir(cache_dir):
            try:
                os.rmdir(cache_dir)
                print(f"已删除空目录: {cache_dir}")
            except Exception as e:
                print(f"删除目录失败 {cache_dir}: {e}")

def get_cache_stats():
    """获取缓存统计信息"""
    cache_dirs = {
        'AI标签缓存': 'ai_label_cache',
        '翻译缓存': 'translation_cache'
    }
    
    print("缓存统计信息:")
    print("=" * 50)
    
    total_files = 0
    total_size = 0
    
    for name, cache_dir in cache_dirs.items():
        if os.path.exists(cache_dir):
            files = os.listdir(cache_dir)
            file_count = len(files)
            dir_size = sum(os.path.getsize(os.path.join(cache_dir, f)) for f in files if os.path.isfile(os.path.join(cache_dir, f)))
            
            total_files += file_count
            total_size += dir_size
            
            print(f"{name}: {file_count} 个文件, {dir_size / 1024:.2f} KB")
        else:
            print(f"{name}: 目录不存在")
    
    print("=" * 50)
    print(f"总计: {total_files} 个文件, {total_size / 1024:.2f} KB")

def main():
    """主函数"""
    print("🧹 缓存清理工具")
    print("=" * 50)
    
    # 显示当前缓存统计
    get_cache_stats()
    
    # 清理过期缓存
    print("\n开始清理过期缓存...")
    clean_expired_cache('ai_label_cache', max_age_days=30)
    clean_expired_cache('translation_cache', max_age_days=30)
    
    # 清理空目录
    print("\n清理空目录...")
    clean_empty_cache_dirs()
    
    # 显示清理后的统计
    print("\n清理后的缓存统计:")
    get_cache_stats()
    
    print("\n✅ 缓存清理完成！")

if __name__ == "__main__":
    main() 