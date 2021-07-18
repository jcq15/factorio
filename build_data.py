import xlrd
import json

def load_data(file):
    workbook = xlrd.open_workbook(file)

    ### recipe ###
    recipe = workbook.sheet_by_index(0)      # 第一张表
    recipes = []
    nrows = recipe.nrows
    for i in range(1, nrows):
        # ['', '1 铁板；1 铁齿轮', '2 基础传送带', 0.5, '制造台']
        value = recipe.row_values(i)
        
        input_ = value[1].split('；')    # '1 铁板；1 铁齿轮'
        input_ = [i.split(' ')[::-1] for i in input_]
        # print(input_)  # [['铁板', '1'], ['铁齿轮', '1']]

        output = value[2].split('；')
        output = [i.split(' ')[::-1] for i in output]

        d = {
            'name': value[5],                # 主产物
            'id': value[0],
            'input': input_,
            'output': output,
            'place': value[4],
            'time': value[3],            # 完成一个配方要多少秒
        }
        # print(d)
        recipes.append(d)
    
    ### fuel ###
    fuel = workbook.sheet_by_index(1)      # fuel
    fuels = [
        {
            'name': fuel.row_values(i)[0],
            'energy': fuel.row_values(i)[1],   # MJ
        }
        for i in range(1, fuel.nrows)
    ]

    ### machine ###
    machine = workbook.sheet_by_index(2)
    machines = [
        {
            'name': machine.row_values(i)[0],
            'speed': machine.row_values(i)[1],
            'power': machine.row_values(i)[2],
            'category': machine.row_values(i)[3],
            'energy': machine.row_values(i)[4],
        }
        for i in range(1, machine.nrows)
    ]

    # 组装成字典吧
    recipe = {}
    for r in recipes:
        recipe[r['name']] = r
    fuel = {}
    for f in fuels:
        fuel[f['name']] = f
    machine = {}
    for m in machines:
        machine[m['name']] = m
    return recipe, fuel, machine


if __name__ == '__main__':
    recipe, fuel, machine = load_data('data.xlsx')
    print(recipe)
    # print(fuel)  # [{'name': '煤矿', 'energy': 4.0}]

    # build 'static/js/recipe_data.json'
    recipe_data = []

    for r in recipe.values():
        m = []
        for mm in machine.values():
            if mm['category'] == r['place']:
                if mm['energy'] == '可燃燃料':
                    # 叉乘，加上燃料名
                    for f in fuel.values():
                        m.append({'n': mm['name'] + '(%s)' % f['name']})
                else:
                    m.append({'n': mm['name']})

        d = {
            'n': r['name'],
            's': m
        }

        recipe_data.append(d)
    
    with open('static/js/recipe_data.json', 'w', encoding='utf-8') as f:
        json.dump(recipe_data, f, ensure_ascii=False)
    