import * as fs from 'fs';
import * as Types from './dto';

function loadConfig(): Types.Config {
    const strConfig = fs.readFileSync('./config.json', 'utf-8');
    const config: Types.Config = JSON.parse(strConfig);
    return config;
}


