import http.cookiejar
import urllib.request
import sys
import io
import json
if __name__ == '__main__':
    # cookie = http.cookiejar.CookieJar()
    # cookie.set(cookieName, uv, 2678400)
    # 改变标准输出的默认编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
    # 登录时需要POST的数据
    data = {'username': 'common',
            'password': '888888',}
    post_data = urllib.parse.urlencode(data).encode('utf-8')
    # 设置请求头
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    }
    # 登录时表单提交到的地址（用开发者工具可以看到）
    login_url = 'http://log-list.server.nubia.cn/login/check.do'
    # 构造登录请求
    req = urllib.request.Request(login_url, headers=headers, data=post_data)
    # 构造cookie
    cookie = http.cookiejar.CookieJar()
    # 由cookie构造opener
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
    # 发送登录请求，此后这个opener就携带了cookie，以证明自己登录过
    resp = opener.open(req)
    print(resp.read().decode('utf-8'))
    # cookie['task_username']='common'
    # cookie.set(cookieName, uv, 2678400);
    #登录后才能访问的网页
    order='asc'
    limit='15'
    offset=1
    jiraId='LOG-67680'
    productVersion='NX629J_Z0_CN_VLF0P_V236'
    hasFile='Y'
    url = 'http://log-list.server.nubia.cn/log/list.do?order=asc&limit=15&offset=1&jiraId=LOG-67680&productVersion=NX629J_Z0_CN_VLF0P_V236&hasFile=Y'
    #构造访问请求
    req = urllib.request.Request(url, headers = headers)
    resp = opener.open(req)
    text = json.loads(resp.read().decode('utf-8'))
    print(text)
    print(text['code'])
    print(text['message'])
    print(text['data'])
    print(text['data']['total'])
    print(text['data']['offset'])
    print(text['data']['limit'])
    print(text['data']['sort'])
    for row in text['data']['rows']:
        print(row['hbaseRowid'])
        print(row['imei'])
        print(row['rooted'])
        print(row['keyInfo'])
    exit(0)
    url = 'http://log-list.server.nubia.cn/log/download/bxoICc.RiYQvnJ.do'

    req = urllib.request.Request(url, headers = headers)
    resp = opener.open(req)
    data = resp.read()
    with open("bxoICc.RiYQvnJ.zip", "wb") as code:
        code.write(data)