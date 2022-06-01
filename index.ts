import * as fs from 'fs';
import * as Types from './dto';
import fetch from 'node-fetch';

const strConfig = fs.readFileSync('./config.json', 'utf-8');
const config: Types.Config = JSON.parse(strConfig);

function ServerChanPush(key: string, title: string, content: string) {
    let url = `https://sctapi.ftqq.com/${key}.send`;
    let data = { 'title': title, 'desp': content }
    fetch(url, {
        method: 'post',
        headers: { 'Content-type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        else {
            console.log('Server酱推送失败 - 网络原因');
            console.log(response);
            return <Types.ServerChanResponse>{ code: -1 }
        }
    }).then(data => {
        let scResp = data as Types.ServerChanResponse;
        if (scResp.code == 0 && scResp.data.errno == 0) {
            console.log('Server酱推送成功');
            console.log(scResp);
        }
        else {
            console.log('Server酱推送失败 - 其他原因');
            console.log(data);
        }
    });
}

function PushDeerPush(key: string, title: string, content: string) {
    let data = { 'pushkey': key, 'text': title, 'desp': content, 'type': 'markdown' };
    fetch('https://api2.pushdeer.com/message/push', {
        method: 'post',
        headers: { 'Content-type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        else {
            console.log('PushDeer推送失败 - 网络原因');
            console.log(response);
            return <Types.PushDeerResponse>{ code: -1 }
        }
    }).then(data => {
        let scResp = data as Types.PushDeerResponse;
        if (scResp.code == 0) {
            console.log('PushDeer推送成功');
            console.log(scResp);
        }
        else {
            console.log('PushDeer推送失败 - 其他原因');
            console.log(data);
        }
    });
}
