enum PushType {
    ServerChan = 'serverchan',
    PushDeer = 'pushdeer'
}

interface Config {
    push: {
        name: string,
        type: PushType,
        key: string
    }[],
    accounts: {
        name: string,
        enable: boolean,
        bduss: string,
        stoken: string,
        push: string[]
    }[]
}

interface ServerChanResponse {
    code: number,
    message: string,
    data: {
        pushid: string,
        readkey: string,
        error: string,
        errno: number
    }
}

interface PushDeerResponse {
    code: number,
    content: {
        result: string[]
    }
}

export { PushType, Config, ServerChanResponse, PushDeerResponse };