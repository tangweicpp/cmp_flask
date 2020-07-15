'''
@File    :   handle.py
@Time    :   2020/07/09 15:30:00
@Author  :   Tang wei
@Version :   1.0
@Contact :   wei.tang_ks@ht-tech.com
@License :   (C)Copyright 2020-2021
@Desc    :   None
'''
import connect_db as conn
import time
import os
import logging
import pandas as pd
import numpy as np
import json
import re


logging.basicConfig(level=logging.INFO, filename='erp.txt',
                    format='%(asctime)s :: %(funcName)s :: %(levelname)s :: %(message)s')


# Check username and password
def check_account(username, password):
    if not (username and password):
        print('用户名或密码为空')
        return False

    sql = "select 用户号 from erpbase..tblOperatorData where 用户号 = '%s' and 密码= '%s' " % (
        username, password)
    results = conn.MssConn.query(sql)
    if not results:
        print('查询不到数据')
        return False
    return True


# Get customer list
def get_custcode_list():
    jsonData = []

    sql = "SELECT DISTINCT CUSTOMERSHORTNAME FROM TBLTSVNPIPRODUCT ORDER BY CUSTOMERSHORTNAME "
    results = conn.OracleConn.query(sql)
    for row in results:
        result = {}
        result['value'] = str(row[0])
        result['label'] = str(row[0])

        jsonData.append(result)
    return jsonData


# Get customer po template
def get_po_template(custcode):
    if not custcode:
        print('客户代码不可为空')
        return []

    jsonData = []
    sql = "SELECT CUST_CODE,TEMPLATE_FILE ,TEMPLATE_PIC ,KEY_LIST ,FILE_LEVEL,FILE_URL,ACCEPT,TEMPLATE_ID FROM CMP_CUST_PO_TEMPLATE WHERE CUST_CODE  = '%s'" % (
        custcode)
    results = conn.OracleConn.query(sql)
    for row in results:
        result = {}
        result['file_name'] = str(row[1])
        result['img_url'] = str(row[2])
        result['file_key'] = str(row[3])
        result['level'] = str(row[4])
        result['file_url'] = str(row[5])
        result['accept'] = str(row[6])
        result['file_id'] = str(row[7])

        jsonData.append(result)
    return jsonData


# Upload po file
def upload_po_file(f, po_header):
    if not f:
        print('文件不存在')
        return False

    file_dir = os.path.join(os.getcwd(), 'uploads/po/' +
                            po_header['po_type']+'/'+po_header['cust_code'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    file_path = os.path.join(file_dir, f.filename)
    f.save(file_path)

    parse_po_file(file_path, po_header)
    return True


# Parse po file
def parse_po_file(file_name, po_header):
    po_dic = get_po_config(po_header)
    if not po_dic:
        return

    file_type = po_dic['file_type']
    if file_type == 'xlsx':
        parse_xlsx_file(file_name, po_header, po_dic)


# Get Json config
def get_po_config(po_header):
    sql = "SELECT TEMPLATE_CONFIG FROM CMP_CUST_PO_TEMPLATE WHERE TEMPLATE_ID  = %s" % (
        po_header['template_id'])
    results = conn.OracleConn.query(sql)
    if not results:
        print("无法获取配置文件")
        return False
    template_config = results[0][0]
    file_dir = os.path.join(os.getcwd(), template_config)
    # print("获取到配置文件", file_dir)

    f = open(file_dir, 'r', encoding="utf-8")
    po_dic = json.load(f)
    return po_dic


# Parse xlsx file
def parse_xlsx_file(file_name, po_header, po_dic):
    df = pd.DataFrame(pd.read_excel(file_name, header=None))
    keys = po_dic['file_keys']
    po_data = []
    for index, row in df.iterrows():
        if index == 0:
            continue

        po_row_data = {}
        po_row_data['po_id'] = str(
            row[keys['po_id']['position']['col']-1]).strip()
        po_row_data['fab_device'] = str(
            row[keys['fab_device']['position']['col']-1]).strip()
        po_row_data['customer_device'] = str(
            row[keys['customer_device']['position']['col']-1]).strip()
        po_row_data['lot_id'] = str(
            row[keys['lot_id']['position']['col']-1]).strip()
        po_row_data['wafer_id'] = str(
            row[keys['wafer_id']['position']['col']-1]).strip()
        po_row_data['wafer_qty'] = str(
            row[keys['wafer_qty']['position']['col']-1]).strip()
        # print(po_row_data)
        po_data.append(po_row_data)

    print(po_data)
    check_po_data(po_header, po_dic, po_data)
    save_po_data(po_header, po_dic, po_data)


# Check po data
def check_po_data(po_header, po_dic, po_data):
    pass


# Save po data
def save_po_data(po_header, po_dic, po_data):
    for item in po_data:
        wafer_id_list = get_wafer_list(item['wafer_id'])
        print(wafer_id_list)


# Get list
def get_wafer_list(wafer_str):
    wafer_str_new = re.sub(r'[_~-]', ' _ ', wafer_str)
    pattern = re.compile(r'[A-Za-z0-9_]+')
    result1 = pattern.findall(wafer_str_new)

    # extend
    for i in range(1, len(result1)-1):
        if result1[i] == '_':
            if result1[i-1].isdigit() and result1[i+1].isdigit():
                bt = []
                if int(result1[i-1]) < int(result1[i+1]):
                    for j in range(int(result1[i-1])+1, int(result1[i+1])):
                        bt.append(f'{j}')
                else:
                    for j in range(int(result1[i-1])-1, int(result1[i+1]), -1):
                        bt.append(f'{j}')
                result1.extend(bt)

    # remove '_'
    result2 = sorted(set(result1), key=result1.index)
    if '_' in result2:
        result2.remove('_')

    return result2
