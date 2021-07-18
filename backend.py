from re import M
from flask import Flask
from flask import request, abort
import json
import uuid
from flask import render_template
import build_data

app = Flask(__name__)
recipe, fuel, machine = build_data.load_data('data.xlsx')    # 加载数据巨巨巨

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/save', methods=['POST'])
def save():
    # data = request.get_json()['data']
    # print(data)
    data = request.get_json()
    filename = 'static/configs/%s.json' % uuid.uuid4()
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False))

    return filename

# 上传文件，原样返回
@app.route('/upload', methods=['POST'])
def upload():
    try:
        f = request.files['file']
        data = json.load(f)
    except:
        return 'fuck'
    else:
        return json.dumps(data, ensure_ascii=False)


# 计算消耗，返回[{'name': '铁板','consume': 100, 'produce': 98},]
@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    data = data['data']

    outcome = {
        '电': {'name': '电', 'consume': 0, 'produce': 0},
    }

    #try:
    # 一条一条看，先看消耗，再看生产，最后看能源
    # [{"recipe": "钢材", "machine": "石炉(煤矿)", "num": ""}, {"recipe": "请选择", "machine": "", "num": ""}]
    for d in data:
        num = int(d['num'])             # 装机数
        r = recipe[d['recipe']]         # 配方
        # r = {'name': '基础传送带', 'id': 1.0, 'input': [['铁板', '1'], ['铁齿轮', '1']], 'output': [['基础传送带', '2']], 'place': '组装机', 'time': 0.5}
        m_name = d['machine'].split('(')[0]     # 机器名
        real_time = r['time'] / machine[m_name]['speed']
        npm = num * 60 / real_time         # 每分钟多少组

        # 处理消耗
        i = r['input']
        for item in i:
            if not item[0]:
                continue            # 没有输入
            # item[0] 铁板 item[1] 数量
            if item[0] in outcome:
                outcome[item[0]]['consume'] += float(item[1]) * npm
            else:
                outcome[item[0]] = {
                    'name': item[0],
                    'consume': float(item[1]) * npm,
                    'produce': 0,
                }
        # 处理生产
        o = r['output']
        for item in o:
            if not item[0]:
                continue       # 没有输出
            if item[0] in outcome:
                outcome[item[0]]['produce'] += float(item[1]) * npm
            else:
                outcome[item[0]] = {
                    'name': item[0],
                    'consume': 0,
                    'produce': float(item[1]) * npm,
                }
        # 处理能源，电的单位是 kW，燃料的单位仍然是 npm
        if machine[m_name]['energy'] == '电力':
            outcome['电']['consume'] += num * machine[m_name]['power']
        else:
            # 烧燃料
            f = d['machine'].split('(')[1][:-1]                  # 燃料名
            temp_num = num * machine[m_name]['power'] * 0.06 / fuel[f]['energy']     # 每分钟多少个
            if f in outcome:
                outcome[f]['consume'] += temp_num
            else:
                outcome[f] = {
                    'name': f,
                    'consume': temp_num,
                    'produce': 0,
                }
    
    print(outcome)
    return json.dumps(outcome, ensure_ascii=False)
    #except Exception as e:
    #    abort('pat pat')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)