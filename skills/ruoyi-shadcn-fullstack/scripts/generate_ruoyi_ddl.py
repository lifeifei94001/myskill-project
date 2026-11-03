#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper script to generate RuoYi-compliant MySQL DDL and permission menu SQL
from a simple field specification.
"""

import sys
import json
import argparse

def generate_ddl(table_name, table_comment, fields, primary_key="id"):
    sql_lines = []
    sql_lines.append(f"-- ----------------------------")
    sql_lines.append(f"-- Table structure for {table_name}")
    sql_lines.append(f"-- ----------------------------")
    sql_lines.append(f"DROP TABLE IF EXISTS `{table_name}`;")
    sql_lines.append(f"CREATE TABLE `{table_name}` (")
    
    col_defs = []
    col_defs.append(f"  `{primary_key}` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID'")
    
    for f in fields:
        fname = f.get("name")
        if fname == primary_key:
            continue
        ftype = f.get("type", "varchar(255)")
        fnullable = "" if f.get("required", False) else "DEFAULT NULL"
        if f.get("required", False):
            fnullable = "NOT NULL"
        fcomment = f.get("comment", "")
        fdefault = f.get("default")
        
        default_str = f"DEFAULT '{fdefault}'" if fdefault is not None else fnullable
        col_defs.append(f"  `{fname}` {ftype} {default_str} COMMENT '{fcomment}'")
        
    # Standard RuoYi audit columns
    col_defs.append(f"  `status` char(1) DEFAULT '0' COMMENT '状态（0正常 1停用）'")
    col_defs.append(f"  `del_flag` char(1) DEFAULT '0' COMMENT '删除标志（0代表存在 2代表删除）'")
    col_defs.append(f"  `create_by` varchar(64) DEFAULT '' COMMENT '创建者'")
    col_defs.append(f"  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'")
    col_defs.append(f"  `update_by` varchar(64) DEFAULT '' COMMENT '更新者'")
    col_defs.append(f"  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'")
    col_defs.append(f"  `remark` varchar(500) DEFAULT NULL COMMENT '备注'")
    col_defs.append(f"  PRIMARY KEY (`{primary_key}`)")
    
    sql_lines.append(",\n".join(col_defs))
    sql_lines.append(f") ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COMMENT='{table_comment}';")
    return "\n".join(sql_lines)

def generate_menu_sql(parent_id, menu_name, module_name, business_name):
    """
    Generate RuoYi sys_menu insert statements for standard CRUD permissions.
    """
    perm_prefix = f"{module_name}:{business_name}"
    return f"""
-- ----------------------------
-- RuoYi Menu & Permissions for {menu_name}
-- ----------------------------
-- 菜单 SQL
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('{menu_name}', {parent_id}, 1, '{business_name}', '{module_name}/{business_name}/index', 1, 0, 'C', '0', '0', '{perm_prefix}:list', '#', 'admin', sysdate(), '', null, '{menu_name}菜单');

-- 按钮权限 SQL (查询、新增、修改、删除、导出)
SELECT @parentId := LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('{menu_name}查询', @parentId, 1, '#', '', 1, 0, 'F', '0', '0', '{perm_prefix}:query', '#', 'admin', sysdate(), '', null, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('{menu_name}新增', @parentId, 2, '#', '', 1, 0, 'F', '0', '0', '{perm_prefix}:add', '#', 'admin', sysdate(), '', null, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('{menu_name}修改', @parentId, 3, '#', '', 1, 0, 'F', '0', '0', '{perm_prefix}:edit', '#', 'admin', sysdate(), '', null, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('{menu_name}删除', @parentId, 4, '#', '', 1, 0, 'F', '0', '0', '{perm_prefix}:remove', '#', 'admin', sysdate(), '', null, '');

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('{menu_name}导出', @parentId, 5, '#', '', 1, 0, 'F', '0', '0', '{perm_prefix}:export', '#', 'admin', sysdate(), '', null, '');
"""

def main():
    parser = argparse.ArgumentParser(description="Generate RuoYi DDL & Menu SQL")
    parser.add_argument("--table", required=True, help="Table name, e.g. village_villager")
    parser.add_argument("--comment", required=True, help="Table comment, e.g. 村民档案表")
    parser.add_argument("--module", default="village", help="Module name, e.g. village")
    parser.add_argument("--business", default="villager", help="Business name, e.g. villager")
    args = parser.parse_args()

    sample_fields = [
        {"name": "name", "type": "varchar(50)", "required": True, "comment": "姓名"},
        {"name": "id_card", "type": "varchar(18)", "required": True, "comment": "身份证号"},
        {"name": "phone", "type": "varchar(20)", "required": False, "comment": "联系手机"},
        {"name": "gender", "type": "char(1)", "default": "0", "comment": "性别（0男 1女 2未知）"}
    ]

    ddl = generate_ddl(args.table, args.comment, sample_fields)
    menu_sql = generate_menu_sql(1, args.comment, args.module, args.business)
    print(ddl)
    print(menu_sql)

if __name__ == "__main__":
    main()
