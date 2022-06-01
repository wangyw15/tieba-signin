import fs = require('fs');
import * as Types from './dto';
//const fetch = (...args: any[]) => import('node-fetch').then(({default: fetch}) => fetch(...args));
import { RequestInfo, RequestInit } from 'node-fetch';
const fetch = (url: RequestInfo, init?: RequestInit) => import('node-fetch').then(({ default: fetch }) => fetch(url, init));

const strConfig = fs.readFileSync('./config.json', 'utf-8');
const config: Types.Config = JSON.parse(strConfig);

function ServerChanPush(key: string, title: string, content: string) {
    let url = `https://sctapi.ftqq.com/${key}.send`;
    let data = { 'title': title, 'desp': content }
    fetch(url, {
        method: 'post',
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

ServerChanPush('SCT18640Tb1MssJyG2cHfMdngQnycG4Rr', 'test', 'hello');