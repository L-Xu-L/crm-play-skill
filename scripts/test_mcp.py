#!/usr/bin/env python3
"""
CRM MCP Server 测试脚本
用于验证 MCP Server 是否正常工作
"""

import json
import sys
import requests

def test_search(url: str, profile: str, limit: int = 10):
    """测试搜索客户画像"""
    print(f"\n=== 测试 search_customer_profile ===")
    print(f"画像: {profile}")
    print(f"条数: {limit}")
    
    # MCP 调用格式
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_customer_profile",
            "arguments": {
                "profile_description": profile,
                "limit": limit
            }
        }
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=30)
        result = resp.json()
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return result
    except Exception as e:
        print(f"错误: {e}")
        return None

def test_import(url: str, customers: list):
    """测试批量导入"""
    print(f"\n=== 测试 batch_import_customer ===")
    print(f"客户数: {len(customers)}")
    
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "batch_import_customer",
            "arguments": {
                "customers": customers
            }
        }
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=30)
        result = resp.json()
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return result
    except Exception as e:
        print(f"错误: {e}")
        return None

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:9026"
    
    print(f"测试 CRM MCP Server: {url}")
    
    # 测试搜索
    test_search(url, "日本地区的酒店客户", 5)
    
    # 测试导入（使用测试数据）
    test_customers = [
        {
            "name": "测试公司",
            "contact_name": "张三",
            "contact_email": f"test_{int(__import__('time').time())}@example.com",
            "contact_phone": "13800138000",
            "contact_phone_prefix": "+86",
            "country_code": "CN",
            "address": "北京市朝阳区",
            "remark": "测试导入"
        }
    ]
    test_import(url, test_customers)

if __name__ == "__main__":
    main()
