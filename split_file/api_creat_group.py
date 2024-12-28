import requests
import pandas as pd

import math
import os
from datetime import datetime
import random
import time

#創建邀請組
def create_single_invitation_group(creator_ids, batch_num, round_num):
    """
    创建单个邀请组
    Args:
        creator_ids: 创作者ID列表
        batch_num: 批次号
        round_num: 轮次号
    Returns:
        tuple: (bool, list) - (是否成功, 失败的creator_ids)
    """
    try:
        # 获取当前日期，格式化为"月.日"
        current_date = datetime.now().strftime("%m.%d")
        
        # 构建查询参数列表
        query_params = [
            ('name', f'_2{current_date}_r{round_num}_b{batch_num}'),
            ('target_commission', '2000'),
            ('email', 'ENVIPRO@WOWORLDTECH.COM'),
            ('end_time', '35')
        ]
        
        # 添加多个product_ids
        product_ids = [
            '1729772778618786084',
            '1729574328904159524',
            '1729574340770107684',
            '1729574337370493220'
        ]
        for product_id in product_ids:
            query_params.append(('product_ids', product_id))
        
        # 添加creator_ids
        for creator_id in creator_ids:
            query_params.append(('creator_ids', str(creator_id)))
        
        # API URL
        url = 'http://192.168.0.123:8080/api/creator/create_group'

        
        # 发送POST请求，使用params参数
        response = requests.post(url, params=query_params)
        
        # 检查是否是服务器内部错误
        if response.status_code == 500 or response.text == 'Internal Server Error':
            print("\n检测到服务器内部错误，程序将终止")
            
            # 获取当前时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unprocessed_file = f'unprocessed_creators_{timestamp}.xlsx'
            
            # 保存未处理的创作者ID
            unprocessed_df = pd.DataFrame({'creator_oecuid': creator_ids})
            unprocessed_df.to_excel(unprocessed_file, index=False)
            
            print(f"未处理的创作者名单已保存到：{unprocessed_file}")
            print(f"未处理的creator数量：{len(creator_ids)}")
            
            # 退出程序
            import sys
            sys.exit(1)

        try:
            response_data = response.json()
        except ValueError as e:
            print(f"JSON解析失败：{str(e)}")
            print(f"原始响应内容：{response.text}")
            
            # 如果是服务器内部错误，直接返回False
            if response.text == 'Internal Server Error':
                return False, creator_ids
                
            return False, creator_ids
            
        # 判断是否成功
        success = (response.status_code == 200 and 
                  response_data.get('code') == 0 and 
                  response_data.get('message') == 'success')
        
        if success:
            invitation_data = response_data.get('data', {}).get('invitation')
            if invitation_data:
                invitation_id = invitation_data.get('id')
                print(f"第{round_num}轮第{batch_num}批次邀请组创建成功！")
                print(f"邀请组ID: {invitation_id}")
                return True, []
            else:
                # 处理冲突的创作者
                conflict_list = response_data.get('data', {}).get('conflict_list', [])
                if conflict_list:
                    print(f"警告：发现{len(conflict_list)}个冲突的创作者")
                    conflicted_creator_ids = set()  # 使用集合存储冲突的creator_ids
                    
                    for conflict in conflict_list:
                        creator_list = conflict.get('creator_id_list', [])
                        for creator in creator_list:
                            base_info = creator.get('base_info', {})
                            creator_id = base_info.get('creator_oec_id')
                            if creator_id:
                                conflicted_creator_ids.add(creator_id)
                                print(f"创作者 {base_info.get('nick_name')} (ID: {creator_id}) 已在组 {conflict.get('name')} 中")
                    
                    # 从当前批次中移除冲突的创作者
                    non_conflicted_creators = [cid for cid in creator_ids if cid not in conflicted_creator_ids]
                    
                    if non_conflicted_creators:
                        print(f"移除{len(conflicted_creator_ids)}个冲突创作者后，尝试重新创建组...")
                        return create_single_invitation_group(non_conflicted_creators, batch_num, round_num)
                    else:
                        print("当前批次中所有创作者都存在冲突")
                        return False, creator_ids
                else:
                    print(f"第{round_num}轮第{batch_num}批次创建失败：响应数据格式异常")
                    print(f"响应内容：{response_data}")
                    return False, creator_ids
        else:
            print(f"第{round_num}轮第{batch_num}批次创建失败")
            print(f"状态码：{response.status_code}")
            print(f"响应内容：{response_data}")
            
            if response_data.get('code') == 50001702:
                print(f"原因：批次中包含不可用的创作者或产品")
            
            return False, creator_ids
            
    except Exception as e:
        print(f"第{round_num}轮第{batch_num}批次处理时发生错误：{str(e)}")
        print(f"错误类型: {type(e)}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return False, creator_ids

def process_batch(creator_ids, batch_size, round_num):
    """
    处理一轮批次发送
    """
    failed_creators = []
    success_count = 0
    fail_count = 0
    
    total_creators = len(creator_ids)
    total_batches = math.ceil(total_creators / batch_size)
    
    print(f"\n开始第{round_num}轮处理（批次大小：{batch_size}）")
    print(f"待处理creator数量：{total_creators}")
    print(f"批次数：{total_batches}")
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, total_creators)
        current_batch = creator_ids[start_idx:end_idx]
        
        print(f"\n处理第{round_num}轮第{batch_num + 1}批次，包含{len(current_batch)}个creator_id")
        success, failed_ids = create_single_invitation_group(current_batch, batch_num + 1, round_num)
        
        if success:
            success_count += 1
        else:
            fail_count += 1
            failed_creators.extend(failed_ids)
            
        # 每个批次处理完后统一睡眠25秒
        print("批次处理完成，等待25秒...")
        time.sleep(25)
    
    print(f"\n第{round_num}轮处理完成")
    print(f"成功批次：{success_count}")
    print(f"失败批次：{fail_count}")
    print(f"失败的creator数量：{len(failed_creators)}")
    
    return failed_creators

def create_invitation_groups(file_path):
    """
    批量创建邀请组，多轮处理
    """
    try:
        # 文件检查
        if not os.path.exists(file_path):
            print(f"错误：文件 '{file_path}' 不存在")
            return
        if not file_path.endswith(('.xlsx', '.xls')):
            print("错误：文件必须是Excel文件（.xlsx或.xls格式）")
            return
            
        # 读取Excel文件
        # print(f"正在读取文件：{file_path}")
        df = pd.read_excel(file_path)
        
        if 'creator_oecuid' not in df.columns:
            print("错误：Excel文件中未找到'creator_oecuid'列")
            return
            
        # 直接将creator_oecuid列转换为字符串列表
        creator_ids = df['creator_oecuid'].astype(str).tolist()
        # print("读取的creator_ids示例：", creator_ids[:5])  # 打印前5个ID用于验证
        
        # 定义每轮的批次大小
        batch_sizes = [50, 30, 10, 1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        #多轮处理
        for round_num, batch_size in enumerate(batch_sizes, 1):
            if not creator_ids:  # 如果没有待处理的creator_ids，退出
                print("\n所有creator_ids处理完成！")
                break

            failed_creators = process_batch(creator_ids, batch_size, round_num)

            if not failed_creators:
                print(f"\n第{round_num}轮全部处理成功！")
                break

            # 更新待处理的creator_ids为本轮失败的ids
            creator_ids = failed_creators

        # 如果最后还有失败的，保存到文件
        if creator_ids:
            failed_file = f'failed_creators_{timestamp}.xlsx'
            failed_df = pd.DataFrame({'creator_oecuid': creator_ids})
            failed_df.to_excel(failed_file, index=False)
            print(f"\n以下creator_ids在所有轮次中都失败了，已保存到：{failed_file}")
            print(f"完全失败的creator数量：{len(creator_ids)}")
            print("这些ID可能存在严重问题，建议人工检查")
        
    except pd.errors.EmptyDataError:
        print("错误：Excel文件为空")
    except Exception as e:
        print(f"处理过程中发生错误：{str(e)}")

if __name__ == "__main__":
    file_path = '12.28llist.xlsx'
    create_invitation_groups(file_path)
