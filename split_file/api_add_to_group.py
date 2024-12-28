import requests
import pandas as pd  # 添加 pandas 库用于读取 Excel 文件

#添加達人到邀請組
def add_creators_to_group(group_id, creator_ids_file):

    # 基础URL
    base_url = 'http://192.168.0.123:8080/api/creator/add_creators'
    
    # 读取Excel文件中的creator_ids
    try:
        # 读取Excel文件
        df = pd.read_excel(creator_ids_file)
        
        # 假设creator_ids在第一列，获取所有非空值
        creator_ids = df.iloc[:, 0].dropna().astype(str).tolist()
        
        if not creator_ids:
            print("错误：文件中没有找到有效的creator_ids")
            return None
            
    except FileNotFoundError:
        print(f"错误：找不到文件 {creator_ids_file}")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return None

    # 构建请求参数
    params = {
        'group_id': group_id,
        'creator_ids': creator_ids
    }

    try:
        # 用POST请求
        response = requests.post(base_url, params=params)
        
        # 打印请求信息以便调试
        # print(f"请求URL: {response.url}")
        # print(f"请求参数: {params}")
        print(f"响应状态码: {response.status_code}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {str(e)}")
        # 打印更详细的错误信息
        if hasattr(e.response, 'text'):
            print(f"错误详情: {e.response.text}")
        return None

if __name__ == '__main__':
    # 示例使用
    #7451815734739175211
    group_id = input("请输入group_id: ")
    #creator_oecuid.xlsx
    creator_ids_file = input("请输入包含creator_ids的文件: ")
    
    result = add_creators_to_group(group_id, creator_ids_file)
    
    if result:
        print("添加成功！API响应：")
        print(result)

    else:
        print("操作失败，请检查错误信息。")
