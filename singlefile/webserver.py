import subprocess
import traceback
from flask import Flask, request, Response, jsonify
import requests
# requests[socks]


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

server = Flask(__name__)

SINGLEFILE_EXECUTABLE = '/node_modules/single-file/cli/single-file'
BROWSER_PATH = '/opt/google/chrome/google-chrome'
singlefile_timeout = 120000
subprocess_timeout = int(singlefile_timeout / 1000) + 2  # 92s
singlefile_timeout_arg = f'--browser-load-max-time={singlefile_timeout}' # singlefile timeout 90s

# server.logger.setLevel('DEBUG')


# def check_site(url, proxies={}, timeout=9):
#     '''return: 
#         1. True, ''
#         2. False, error_str
#     '''
#     default_title = 'empty'
#     headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}
    
#     try:
#         # 先尝试HEAD
#         head_response = requests.head(url, timeout=timeout, headers=headers, proxies=proxies, verify=False)
#         if head_response.status_code < 400 or head_response.status_code == 403:
#             if 'text/html' in head_response.headers.get('Content-Type') or 'text/plain' in head_response.headers.get('Content-Type') or 'application/json' in head_response.headers.get('Content-Type'):
#                 return True, default_title
#             else:
#                 server.logger.debug('[debug] target website may not be html because Content-Type is: ' + head_response.headers.get('Content-Type'))
#                 return False, 'target website may not be html, content-type = '+ head_response.headers.get('Content-Type')
#         else:
#             # print("http head response code = ", head_response.status_code)
#             return False, 'http head response code = '+ str(head_response.status_code)
#     except Exception as e:
#         traceback.print_exc()
#         try:
#             req = requests.get(url, timeout=timeout, proxies=proxies, verify=False)
#             server.logger.debug('[debug] check alive get http code:\t' + str(req.status_code))
#             if req.status_code < 400:
#                 if req.headers.get('Content-Type') in ('text/plain', 'text/html'):
#                     return True, ''
#                 else:
#                     return False, 'target website is not html, content-type = '+ head_response.headers.get('Content-Type')
#             else:
#                 # print('[error] http recv:', req.text)
#                 return False, 'http code = '+ str(req.status_code)
#         except:
#             traceback.print_exc()
#             return False, traceback.format_exc()



def check_site(url, proxies={}, timeout=9):
    '''return: 
        {
            'status':True,
            'error':'',
            'html':''
        }
    '''
    default_title = 'empty'
    headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"}

    try:
        req = requests.get(url, headers=headers, timeout=(timeout, timeout+10), proxies=proxies, verify=False)
        server.logger.debug('[debug] check alive get http code:\t' + str(req.status_code))
        if req.status_code < 400:
            # if req.headers.get('Content-Type') in ('text/plain', 'text/html'):
            return {
                    'status':True,
                    'error':'',
                    'html': req.text
                }
        else:
            print('[error] singlefile server, http recv:', req.text)
            return {
                    'status':False,
                    'error':'http code = '+ str(req.status_code),
                    'html': ''
                }
    except:
        traceback.print_exc()
        return {
                    'status':False,
                    'error':traceback.format_exc(),
                    'html': ''
                }

@server.route('/', methods=['POST'])
def singlefile():
    browser_args = ["--no-sandbox", "--ignore-certificate-errors", "--disable-gpu", "--lang=zh-CN", "--window-size=1920,1080", "--disable-blink-features=AutomationControlled", "--disable-infobars", "--disable-dev-shm-usage", "--disable-setuid-sandbox"]
    try:
        url = request.form.get('url')
        server.logger.debug('[+] get url:\t' + url)
        proxy = request.form.get('proxy')
        new_singlefile_timeout = request.form.get('timeout')
        proxies = {}
        browser_args.append('--user-agent=' + "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")

        if proxy:
            browser_args.append('--proxy-server=' + proxy)
            proxies = {'http':proxy, 'https':proxy}
        if new_singlefile_timeout:
            global singlefile_timeout, subprocess_timeout, singlefile_timeout_arg
            singlefile_timeout = int(new_singlefile_timeout) * 1000
            subprocess_timeout = int(new_singlefile_timeout) + 2
            singlefile_timeout_arg = f'--browser-load-max-time={singlefile_timeout}'

        browser_args = str(browser_args).replace("'", '"')
        
        if url:
            server.logger.debug(" ".join([
                SINGLEFILE_EXECUTABLE,
                singlefile_timeout_arg,
                '--browser-executable-path=' + BROWSER_PATH,
                "--browser-args" , browser_args,
                request.form['url'],
                '--dump-content',
                ]))
            
            check_res = check_site(url, proxies)
            if check_res['status'] == True:
                p = subprocess.Popen([
                    SINGLEFILE_EXECUTABLE,
                    '--browser-executable-path=' + BROWSER_PATH,
                    "--browser-args" , browser_args,
                    request.form['url'],
                    '--load-deferred-images-max-idle-time','3000',
                    '--dump-content',
          
                    ],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    singlefile_html, run_error = p.communicate(timeout=subprocess_timeout)
                except:
                    if p and p.poll() is None:  # 检查进程是否仍在运行
                        server.logger.debug('[debug] singlefile and chrome process still running. try kill')
                        p.terminate()  # 尝试终止进程
                        try:
                            p.wait(timeout=2)  # 等待进程终止，最多等待2秒
                        except subprocess.TimeoutExpired:
                            p.kill()  # 强制杀死进程
                    res = {
                        'url':url,
                        'status': 'fail',
                        'error': f'run singlefile timeout with {singlefile_timeout}ms'
                    }
                    return jsonify(res), 400
                if run_error:
                    res = {
                        'url':url,
                        'status': 'fail',
                        'error': 'run singlefile error: ' + run_error.decode('utf-8', errors='ignore')
                    }
                    return jsonify(res), 400
                
                if b'URL:' in singlefile_html[:10] and b'Stack: ' in singlefile_html[len(url):20]:
                    error = ''
                    try:
                        error = singlefile_html.split(b'Stack: ')[1].split(b'\n')[0].decode('utf-8', errors='ignore')
                    except:
                        error = singlefile_html.decode('utf-8', errors='ignore')
                    res = {
                        'url':url,
                        'status': 'fail',
                        'error': 'singlefile throw error after run: ' + error
                    }
                    return jsonify(res), 400
                else:
                    # all ok!
                    return Response(singlefile_html, content_type='text/html', status=200)
            else:
                res = {
                    'url':url,
                    'status': 'fail',
                    'error': check_res['error']
                }
                return jsonify(res), 400

    except:
        server.logger.debug('[-] error:\t' + traceback.format_exc())
        res = {
            'url':url,
            'status': 'fail',
            'error': traceback.format_exc()
        }
        return jsonify(res), 400

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=80, debug=True)  #debug=True
