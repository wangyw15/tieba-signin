import json
from urllib.parse import quote
from time import sleep
from requests import post, Session

def signin(account):
    '''
    签到
    '''
    ret = {'success': True, 'msg': ''}

    def my_log(msg):
        ret['msg'] += msg + '\n\n'
        print(msg)

    my_log(f"# 配置：{account['name']}")

    # 生成Session
    like_url = 'https://tieba.baidu.com/mo/q/newmoindex'
    sign_url = 'http://tieba.baidu.com/sign/add'
    head = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': f"BDUSS={account['bduss']}; STOKEN={account['stoken']}",
        'Host': 'tieba.baidu.com',
        'Referer': 'http://tieba.baidu.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
        'X-Requested-With': 'XMLHttpRequest'}
    sess = Session()

    # 获取贴吧列表
    forum_info_resp = sess.get(like_url, headers=head).json()
    if not forum_info_resp['no'] == 0:
        ret['success'] = False
        my_log('获取贴吧列表失败')
        my_log(f"```\n{forum_info_resp}\n```")
        return ret

    auto_signed = 0
    already_signed = 0
    failed = 0
    for forum in forum_info_resp['data']['like_forum']:
        if forum['is_sign'] == 0:
            sleep(0.5)
            data = {
                'ie': 'utf-8',
                'kw': forum['forum_name'],
                'tbs': forum_info_resp['data']['tbs']
            }
            signin_resp = sess.post(sign_url, data=data, headers=head).json()
            if signin_resp['no'] == 0:
                auto_signed += 1
                my_log(f"- {forum['forum_name']}")
                my_log(
                    f"  - 第{signin_resp['data']['uinfo']['user_sign_rank']}个签到")
                my_log(
                    f"  - 共签到{signin_resp['data']['uinfo']['total_sign_num']}天")
            else:
                failed += 1
                my_log(f"- {forum['forum_name']}")
                my_log('  - 签到失败')
                my_log(f"```\n{signin_resp}\n```")
        else:
            already_signed += 1
            my_log(f"- {forum['forum_name']}")
            my_log('  - 已经签到过了')
    my_log(
        f"> 共{len(forum_info_resp['data']['like_forum'])}个吧，已签到{already_signed}个，签到成功{auto_signed}个，签到失败{failed}个")
    my_log('---')
    return ret


def serverchan_push(key, title, content):
    '''
    Serverchan推送
    '''
    url = f'https://sctapi.ftqq.com/{key}.send'
    data = {'title': title, 'desp': content}
    resp = post(url=url, data=data).json()
    if resp['data']['errno'] == 0:
        print('Server酱推送成功')
    else:
        print('Server酱推送失败')
        print('-----错误信息-----')
        print(resp)
        print('------------------')


def pushdeer_push(key, title, content):
    '''
    PushDeer推送
    '''
    url = 'https://api2.pushdeer.com/message/push'
    data = {'pushkey': key, 'text': title, 'desp': content, 'type': 'markdown'}
    resp = post(url=url, data=data).json()
    if resp['code'] == 0:
        print('PushDeer推送成功')
    else:
        print('PushDeer推送失败')
        print('-----错误信息-----')
        print(resp)
        print('------------------')


def main():
    '''
    入口
    '''
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        msg = {'all': ''}
        for account in config['accounts']:
            if account['enable']:
                result = signin(account)
                if 'push' in account.keys():
                    for push in account['push']:
                        if not push in msg.keys():
                            msg[push] = ''
                        msg[push] += result['msg'] + '---\n\n'
                else:
                    msg['all'] += result['msg'] + '---\n\n'

        for i in config['push']:
            content = f"> 推送配置名称：{i['name']}\n\n" + msg['all']
            if (not msg['all'] == '') or (i['name'] in msg.keys()):
                if i['name'] in msg.keys():
                    content += msg[i['name']]

                if i['type'] == 'serverchan' and i['enable']:
                    serverchan_push(i['key'], '贴吧自动签到',
                                    f"> 推送配置名称：{i['name']}\n\n" + content)
                if i['type'] == 'pushdeer' and i['enable']:
                    pushdeer_push(i['key'], '贴吧自动签到',
                                  f"> 推送配置名称：{i['name']}\n\n" + content)


def main_handler(event, context):
    '''
    云函数默认入口
    '''
    main()


if __name__ == '__main__':
    main()
