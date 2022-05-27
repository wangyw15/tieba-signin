import json
from time import sleep
from typing import Dict, List
from requests import post, Session
import logging

handler = logging.StreamHandler()
handler.setLevel('DEBUG')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)-9s - %(filename)-8s : %(lineno)4s line - %(message)s'))
logger = logging.getLogger('tieba-signin')
logger.setLevel('DEBUG')
logger.addHandler(handler)


class ForumResult:
    '''
    # 贴吧签到结果
    | 代码 | 结果 |
    | :-: | :-: |
    | 0 | 正常签到 |
    | -1 | 已签到 |
    | 1 | 出错 |
    '''

    def __init__(self, code=0, name='', description='', rank=0, days=0):
        self.name = name
        self.description = description
        self.rank = rank
        self.days = days
    code = 0
    '''
    # 错误代码
    | 代码 | 结果 |
    | :-: | :-: |
    | 0 | 正常签到 |
    | -1 | 已签到 |
    | 1 | 出错 |
    '''
    name = ''
    description = ''
    rank = 0
    days = 0


class SigninResult:
    '''
    总签到结果
    '''

    def __init__(self, code=0, data: List[ForumResult] = None, auto_signed=0, already_signed=0, failed=0):
        self.code = code
        if data is not None:
            self.data = data
        else:
            self.data = []
        self.auto_signed = auto_signed
        self.already_signed = already_signed
        self.failed = failed
    code = 0
    name = ''
    auto_signed = 0
    already_signed = 0
    failed = 0
    data: List[ForumResult] = []

def unicode2chinese(content: str):
    '''
    恢复Unicode转义
    '''
    return content.encode(encoding='utf-8').decode('unicode_escape')

def signin(account):
    '''
    签到
    '''
    ret = SigninResult()
    ret.name = account['name']
    logger.info('正在签到：%s', account['name'])
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
    if forum_info_resp['no'] != 0:
        ret.code = 1
        ret.data.append(ForumResult(
            1, '获取贴吧列表失败', json.dumps(forum_info_resp)))
        logger.error('获取贴吧列表失败')
        logger.exception(forum_info_resp)
        return ret
    # 签到
    for forum in forum_info_resp['data']['like_forum']:
        forum_result = ForumResult(0, forum['forum_name'])
        logger.info('当前贴吧：%s', forum['forum_name'])
        if forum['is_sign'] == 0:
            sleep(0.5)
            data = {
                'ie': 'utf-8',
                'kw': forum['forum_name'],
                'tbs': forum_info_resp['data']['tbs']
            }
            signin_resp = sess.post(sign_url, data=data, headers=head).json()
            if signin_resp['no'] == 0:
                ret.auto_signed += 1
                forum_result.rank = signin_resp['data']['uinfo']['user_sign_rank']
                forum_result.days = signin_resp['data']['uinfo']['total_sign_num']
                logger.info(
                    '第%s个签到', signin_resp['data']['uinfo']['user_sign_rank'])
                logger.info(
                    '共签到%s天', signin_resp['data']['uinfo']['total_sign_num'])
            else:
                ret.failed += 1
                forum_result.code = 1
                forum_result.description = json.dumps(signin_resp)
                logger.error('签到失败')
                logger.exception(signin_resp)
        else:
            ret.already_signed += 1
            forum_result.code = -1
            logger.info('已经签到过了')
        ret.data.append(forum_result)
    logger.info('共%d个吧，已签到%d个，签到成功%d个，签到失败%d个', len(
        forum_info_resp['data']['like_forum']), ret.already_signed, ret.auto_signed, ret.failed)
    return ret


def serverchan_push(key: str, title: str, content: str):
    '''
    Serverchan推送
    '''
    url = f'https://sctapi.ftqq.com/{key}.send'
    data = {'title': title, 'desp': content}
    resp = post(url=url, data=data).json()
    if resp['data']['errno'] == 0:
        logger.info('Server酱推送成功')
    else:
        logger.error('Server酱推送失败')
        logger.exception(resp)


def pushdeer_push(key: str, title: str, content: str):
    '''
    PushDeer推送
    '''
    url = 'https://api2.pushdeer.com/message/push'
    data = {'pushkey': key, 'text': title, 'desp': content, 'type': 'markdown'}
    resp = post(url=url, data=data).json()
    if resp['code'] == 0:
        logger.info('PushDeer推送成功')
    else:
        logger.error('PushDeer推送失败')
        logger.exception(resp)


def generate_markdown(results: List[SigninResult]):
    '''
    生成Markdown
    '''
    ret = ''
    for result in results:
        ret += f"# 配置：{result.name}\n\n"
        if result.code == 0:
            ret += f"> 共{result.failed + result.auto_signed + result.already_signed}个吧，已签到{result.already_signed}个，签到成功{result.auto_signed}个，签到失败{result.failed}个\n\n"
            for forum in result.data:
                ret += f"- {forum.name}\n"
                if forum.code == 0:
                    ret += f"  - 第{forum.rank}个签到\n"
                    ret += f"  - 共签到{forum.days}天\n"
                elif forum.code == 1:
                    ret += '  - 签到失败\n'
                    ret += f"```\n{forum.description}\n```\n"
                elif forum.code == -1:
                    ret += '  - 已签到\n'
            ret += '\n'
        else:
            ret += '> 签到失败\n\n'
            ret += f"```\n{unicode2chinese(result.data[0].description)}\n```\n\n"
    return ret


def main():
    '''
    入口
    '''
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        results: Dict[str, List[SigninResult]] = {}
        for account in config['accounts']:
            if account['enable']:
                result = signin(account)
                if 'push' in account.keys():
                    for push in account['push']:
                        if not push in results.keys():
                            results[push] = []
                        results[push].append(result)
        for i in config['push']:
            if i['name'] in results.keys():
                content = f"> 推送配置名称：{i['name']}\n\n" + \
                    generate_markdown(results[i['name']])
                logger.info('推送到%s', i['name'])
                logger.info('推送内容预览')
                logger.info(content)
                if i['type'] == 'serverchan':
                    serverchan_push(i['key'], '贴吧自动签到', content)
                if i['type'] == 'pushdeer':
                    pushdeer_push(i['key'], '贴吧自动签到', content)


def main_handler(event, context):
    '''
    云函数默认入口
    '''
    main()


if __name__ == '__main__':
    main()
