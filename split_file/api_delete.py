import requests

url = 'http://192.168.0.123:8080/api/deluser/getuser?page=1&size=100'
delete_url = 'http://192.168.0.123:8080/api/deluser/deleteuser?pk='

res = requests.get(url).json()
data = res['data']
ids = []
for i in data:
    ids.append(i['base']['oec_id'])
for j in ids:
    res = requests.delete(delete_url + j).json()
    if res['code'] == 0:
        print(f'删除成功{j}')
    else:
        print(f'删除失败{j}')