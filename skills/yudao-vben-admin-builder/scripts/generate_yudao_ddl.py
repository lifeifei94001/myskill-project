#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_yudao_ddl.py - Helper script to generate standardized MySQL DDL for Yudao (ruoyi-vue-pro).

Ensures all standard audit fields and multi-tenant fields are present:
- id (BIGINT NOT NULL AUTO_INCREMENT)
- tenant_id (BIGINT NOT NULL DEFAULT 0)
- creator (VARCHAR(64) DEFAULT '')
- create_time (DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)
- updater (VARCHAR(64) DEFAULT '')
- update_time (DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
- deleted (BIT(1) NOT NULL DEFAULT b'0')
"""

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def generate_ddl(table_name: str, comment: str, is_tenant: bool = True, fields: list = None) -> str:
    lines = [f"CREATE TABLE `{table_name}` ("]
    lines.append("  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '编号',")
    
    if fields:
        for f in fields:
            # Format: name:type:comment:not_null
            parts = f.split(":")
            col_name = parts[0]
            col_type = parts[1] if len(parts) > 1 else "varchar(255)"
            col_comment = parts[2] if len(parts) > 2 else col_name
            not_null = "NOT NULL" if len(parts) > 3 and parts[3].lower() in ("true", "1", "not_null") else "DEFAULT NULL"
            lines.append(f"  `{col_name}` {col_type} {not_null} COMMENT '{col_comment}',")
    else:
        # Default example fields
        lines.append("  `name` varchar(100) NOT NULL COMMENT '名称',")
        lines.append("  `status` tinyint NOT NULL DEFAULT '0' COMMENT '状态（0开启 1关闭）',")
        lines.append("  `remark` varchar(500) DEFAULT NULL COMMENT '备注',")

    if is_tenant:
        lines.append("  `tenant_id` bigint NOT NULL DEFAULT '0' COMMENT '租户编号',")

    lines.append("  `creator` varchar(64) DEFAULT '' COMMENT '创建者',")
    lines.append("  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',")
    lines.append("  `updater` varchar(64) DEFAULT '' COMMENT '更新者',")
    lines.append("  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',")
    lines.append("  `deleted` bit(1) NOT NULL DEFAULT b'0' COMMENT '是否删除',")
    lines.append("  PRIMARY KEY (`id`),")
    
    if is_tenant:
        lines.append(f"  KEY `idx_tenant_id` (`tenant_id`)")
    else:
        # remove trailing comma from PRIMARY KEY line
        lines[-1] = "  PRIMARY KEY (`id`)"

    lines.append(f") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='{comment}';")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate Yudao-compliant MySQL DDL table structure")
    parser.add_argument("--table", "-t", required=True, help="Table name in module_entity format, e.g., crm_customer")
    parser.add_argument("--comment", "-c", required=True, help="Table comment/description")
    parser.add_argument("--no-tenant", action="store_true", help="Omit tenant_id column (for non-tenant tables)")
    parser.add_argument("--fields", "-f", nargs="*", help="Custom fields in name:type:comment format, e.g. code:varchar(64):编码:1")

    args = parser.parse_args()
    ddl = generate_ddl(args.table, args.comment, is_tenant=not args.no_tenant, fields=args.fields)
    print("\n-- =============================================")
    print(f"-- Yudao Compliant DDL: {args.table}")
    print("-- =============================================")
    print(ddl)

if __name__ == "__main__":
    main()
