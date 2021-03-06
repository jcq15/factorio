// 需在引入 jquery.cxselect.js 之后，调用之前设置
$.cxSelect.defaults.url = recipe_url;
$.cxSelect.defaults.emptyStyle = 'none';

// 传入 jQuery 对象，俺给它绑定 cxSelect
function bindCx(obj) {
    obj.cxSelect({
        url: recipe_url,               // 提示：如果服务器不支持 .json 类型文件，请将文件改为 .js 文件
        selects: ['recipe', 'machine'],  // selects 为数组形式，请注意顺序
        emptyStyle: 'none'
    });
}

// 将当前配置组装成 json
function makeData() {
    var lines = $('#mainbody').find("tr");
    var data = [];
    for (line of lines) {
        var lineData = {
            recipe: $(line).find("select.recipe option:selected").text(),
            machine: $(line).find("select.machine option:selected").text(),
            num: $(line).find("input.num").val(),
        };
        data.push(lineData);
    }
    return data;
}

// 增加一行
function add_tr(recipe = "", machine = "", num = 0) {
    // select 必须放在元素 class='cx' 的内部，不限层级
    // select 的 class 任意取值，也可以附加多个 class，如 class="province otherclass"，在调用时只需要输入其中一个即可，但是不能重复
    var text = `
        <tr class='cx'>
            <td><select class="recipe custom-select" data-value="${recipe}"></select></td>
            <td><select class="machine custom-select" data-value="${machine}"></select></td>
            <td><input type="number" class="form-control num" placeholder="${num}"></td>
            <td><button type="button" class="btn btn-dark del-tr">删除</button></td>
        </tr>
    `;
    var new_tr = $(text);

    $('#mainbody').append(new_tr);

    bindCx(new_tr);                     // 下拉列表绑定动作
    // 行末删除按钮
    new_tr.find('button.del-tr').click(function (event) {
        $(this).parents('tr.cx').remove();
        $('#mainbody').change();        // 触发change事件
    });

    $('#mainbody').change();            // 触发change事件
}

// “新增”按钮
$('#add_one').click(function (event) {
    add_tr();
});

// 保存到文件
// 向后端 post 数据，后端保存后返回链接
$('#save').click(function (event) {
    var data = { data: makeData() };
    console.log(data);

    $.ajaxSetup({ contentType: "application/json; charset=utf-8" });
    $.ajax({
        type: 'POST',
        url: '/save',
        data: JSON.stringify(data),
        success: function (data, status) {
            window.open(data);
        },
    });
})

// 加载数据
function loadData(data) {
    $('#mainbody').empty();
    console.log(data)
    for (d in data) {
        console.log(d);
        add_tr(data[d].recipe, data[d].machine, parseInt(data[d].num));
    }
}

$('#inputGroupFileAddon04').click(function (event) {
    var files = $('#inputGroupFile04').prop('files');
    var data = new FormData();
    data.append('file', files[0]);

    $.ajax({
        url: '/upload',
        type: 'POST',
        cache: false,
        data: data,
        processData: false,
        contentType: false,
    }).done(function (res) {
        // 垃圾JavaScript
        var data = eval("(" + res + ")");
        loadData(data.data);
    }).fail(function (res) {
        console.log('炸了');
    });
});

$(document).ready(function () {
    bsCustomFileInput.init();
});

// 结果那里加一行
function add_res(name, consume, produce) {
    var badge;
    if (produce - consume < -0.1) {
        // 不够
        badge = `<span class="badge badge-danger">不够</span>`;
    } else if (produce - consume > 0.1) {
        badge = `<span class="badge badge-primary">超量</span>`;
    } else {
        badge = `<span class="badge badge-success">牛了</span>`;
    }
    var text = `
        <tr>
            <td>${badge}&nbsp;${name}</td>
            <td>${consume}</td>
            <td>${produce}</td>
        </tr>
    `;
    $('#resultbody').append(text);
}

// 内容改变实时刷新
$('#mainbody').change(function (event) {
    var data = { data: makeData() };
    console.log(data);

    $.ajaxSetup({ contentType: "application/json; charset=utf-8" });
    $.ajax({
        type: 'POST',
        url: '/calculate',
        data: JSON.stringify(data),
        success: function (res, status) {
            // 渲染数据
            var data = eval("(" + res + ")");
            console.log(data);
            $('#resultbody').empty();
            for (d in data) {
                var line = data[d];
                add_res(line.name, line.consume, line.produce);
            }
        },
    });
})