#coding=utf-8
import requests
import os
requests.packages.urllib3.disable_warnings()

SRV_URL = 'https://192.168.31.13'
BEAR_TOKEN = 'cQTXL8hS9ig5Gc1WFEst4ERUXX3Oi_'
proxies = {
    # 'http': 'http://127.0.0.1:8080',
    # 'https': 'http://127.0.0.1:8080'
}

def add_article(file_path):
    '''
    添加一个新的收藏文件。提交方式为多重表单，参数就是下面的files里定义的，认证方式是bearer token。
    接口返回的是json。
    函数返回值是提交成功后返回的id字符串
    '''
    print('添加一个收藏文件..')
    file_name = os.path.basename(file_path)
    files = {   
        'custom_tags':(None,'api,例子'),  # 设置标签，每个标签之间用英文逗号分隔。留空则不设置标签
        'title':(None,''),                  # 设置收藏条目的标题
        'remark':(None,''),                 # 设置备注
        'summary':(None,''),                # 设置摘要
        'user':(None,'admin'),              # 设置上传用户是谁，只能指定有效的用户名
        # 'content':('api上传.docx', open(r'D:\api上传.docx','rb'), 'application/x-zip-compressed') # 上传的文件，只需要修改文件名和文件路径即可
        'content':(file_name, open(file_path, 'rb'), 'application/x-zip-compressed') # 上传的文件
    }
    headers = {
        'Authorization': f'Bearer {BEAR_TOKEN}'
    }

    url = f'{SRV_URL}/article/add/api'
    req = requests.post(url, files=files, verify=False, timeout=30, headers=headers, proxies=proxies)
    print(req.status_code, req.text)
    '''
        返回状态码200，body是json，需要注意的是里面包含一个键值对（id），如果你下一步想要对这个收藏的条目添加附件，就需要这个id：
        {"status": true, "tips": "add success", "id": 381}
    '''
    res = req.json()
    return str(res.get('id'))


def craw_url(craw_url):
    '''
    添加一个新的需要爬取页面的url链接
    '''
    print('添加一个收藏的URL..')
    data = {  
        'custom_tags':(None,'123,1234'),
        'title':(None, ''),
        'remark':(None, ''),
        'summary':(None, ''),
        'user':(None, 'admin'),
        'url':(None, craw_url),
    }
    headers = {
        'Authorization': f'Bearer {BEAR_TOKEN}'
    }
    url = f'{SRV_URL}/url/add/api'
    req = requests.post(url, files=data, verify=False, timeout=30, headers=headers, proxies=proxies)
    print(req.status_code, req.text)


def add_attr(file_path, id):
    '''
    为某个收藏的条目添加一个附件
    '''
    print(f'为id为{id}的收藏条目添加附件..')
    file_name = os.path.basename(file_path)
    headers = {
        'Authorization': f'Bearer {BEAR_TOKEN}'
    }
    url = f'{SRV_URL}/upload_attachments'
    files = [
        ('files', (file_name, open(file_path, 'rb'), 'application/x-zip-compressed')),
    ]
    data = {
        'article_id': id,
        'user':'admin',
    }
    req = requests.post(
        url=url,
        headers=headers,
        files=files,
        data=data,
        verify=False,
        timeout=30,
        proxies=proxies,
    )
    print(req.status_code)
    print(req.text)



def voice2text(id):
    '''
    把指定id的收藏条目（需是音频或视频）进行声音转文本
    '''
    url = f'{SRV_URL}/voiceToWord/{id}'
    req = requests.get(url, verify=False, timeout=30, proxies=proxies)
    print(req.status_code, req.text)


if __name__ == '__main__':
    fid = add_article(r'D:\api上传.docx')
    craw_url('https://www.baidu.com')
    add_attr(r'D:\api上传.docx', fid)
    # voice2text('666')