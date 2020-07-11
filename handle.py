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
def upload_po_file(f, po_data):
    if not f:
        print('文件不存在')
        return False

    file_dir = os.path.join(os.getcwd(), 'uploads/po/' +
                            po_data['po_type']+'/'+po_data['cust_code'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    file_path = os.path.join(file_dir, f.filename)
    f.save(file_path)

    parse_po_file(file_path, po_data)
    return True


# Parse po file
def parse_po_file(file_name, po_data):
    df = pd.DataFrame(pd.read_excel(file_name, header=None))
    # print(df)
    for index, row in df.iterrows():
        # print(index)
        print(row)
        po_id = str(row[2]).strip()
        fab_device = str(row[4]).strip()
        print(po_id, fab_device)
