import json
import re
import time
from tools.des_code import ImgCode
from tools.img_code import createCodeImage
from tools.parameter import RET, MSG
from flask import Flask, render_template, request, jsonify, session, Blueprint, redirect, g
from tools.mysql_tools import SqlData_
from tools.other import now_time, formatCurrency, event_sort, login_required
from tools.redis_tools import redisTool

admin_blueprint = Blueprint('/', __name__, url_prefix='/', )


@admin_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr
    if request.method == 'GET':
        code, img_str = createCodeImage(height=46)
        context = dict()
        string = ImgCode().jiami(code)
        context['img'] = img_str
        context['code'] = string
        try_number = redisTool.string_get(ip)
        if try_number is None:
            try_number = 0
        if int(try_number) >= 3:
            context['drop_status'] = "block"
        else:
            context['drop_status'] = "none"
        return render_template('login.html', **context)
    if request.method == 'POST':
        results = {'code': RET.OK, 'msg': MSG.OK}
        data = json.loads(request.form.get('data'))
        user_name = data.get('user_name')
        user_pass = data.get('pass_word')
        image_real = data.get('image_real')
        image_code = data.get('image_code')
        try:
            try_number = redisTool.string_get(ip)
            if not try_number:
                redisTool.string_set(ip, 1)
            else:
                new_number = int(try_number) + 1
                redisTool.string_set(ip, new_number)

            try_number = redisTool.string_get(ip)
            if int(try_number) > 3:
                # 校验图片验证码
                img_code = ImgCode().jiemi(image_real)
                if image_code.lower() != img_code.lower():
                    results['code'] = 501
                    results['msg'] = '验证码错误！'
                    return jsonify(results)

            # 主账号登录
            user_data = SqlData_.search_user_login(user_name)
            pass_word = user_data.get('password')
            name = user_data.get('name')
            if user_pass == pass_word:
                session['name'] = name
                session.permanent = True
                redisTool.string_del(ip)
                return jsonify(results)
            else:
                results['code'] = RET.SERVERERROR
                results['msg'] = MSG.PSWDERROR
                return jsonify(results)

        except Exception as e:
            results['code'] = RET.SERVERERROR
            results['msg'] = MSG.PSWDERROR
            return jsonify(results)


@admin_blueprint.route('/logout/', methods=['GET'])
@login_required
def logout():
    session.pop('name')
    return redirect('/login/')


@admin_blueprint.route('/change_pass/', methods=['GET', 'POST'])
@login_required
def change_pass():
    if request.method == 'GET':
        return render_template('chang_pass.html')
    if request.method == 'POST':
        data = json.loads(request.form.get('data'))
        old_pass = data.get('old_pass')
        new_pass_one = data.get('new_pass_one')
        new_pass_two = data.get('new_pass_two')
        pass_word = SqlData_.search_field('user_info', 'password', 1)
        results = {'code': RET.OK, 'msg': MSG.OK}
        res = re.match('(?!.*\s)(?!^[\u4e00-\u9fa5]+$)(?!^[0-9]+$)(?!^[A-z]+$)(?!^[^A-z0-9]+$)^.{8,16}$', new_pass_one)
        if not res:
            results['code'] = RET.SERVERERROR
            results['msg'] = '密码不符合要求！'
            return jsonify(results)
        if not (old_pass == pass_word):
            results['code'] = RET.SERVERERROR
            results['msg'] = MSG.PSWDERROR
            return jsonify(results)
        if not (new_pass_one == new_pass_two):
            results['code'] = RET.SERVERERROR
            results['msg'] = '两次密码输入不一致！'
            return jsonify(results)
        try:
            SqlData_.update_password(new_pass_one, 1)
            session.pop('name')
            return jsonify(results)
        except Exception as e:
            results['code'] = RET.SERVERERROR
            results['msg'] = MSG.SERVERERROR
            return jsonify(results)


@admin_blueprint.route('/index/')
@login_required
def index():
    user_name = g.user_name
    content = {
        'user_name': user_name
    }
    return render_template('index.html', **content)


@admin_blueprint.route('/add_order/', methods=['GET', 'POST'])
@login_required
def add_order():
    if request.method == "GET":
        return render_template('add_order.html')
    if request.method == "POST":
        data = json.loads(request.form.get('data'))
        user_name = data.get('user_name')
        phone = data.get('phone')
        address = data.get('address')
        t = now_time()
        SqlData_.insert_order(user_name, phone, address, t, '已下单')
        results = {"code": RET.OK, "msg": MSG.OK}
        return jsonify(results)


@admin_blueprint.route('/order_list/')
@login_required
def order_list():
    page = request.args.get('page')
    limit = request.args.get('limit')
    user_name = request.args.get('user_name')
    phone = request.args.get('phone')
    address = request.args.get('address')
    _status = request.args.get('_status')
    name_sql = ""
    phone_sql = ""
    address_sql = ""
    status_sql = ""
    if user_name:
        name_sql = ' AND user_name LIKE "%{}%"'.format(user_name)
    if phone:
        phone_sql = ' AND phone LIKE "%{}%"'.format(phone)
    if address:
        address_sql = ' AND address LIKE "%{}%"'.format(address)
    if _status:
        status_sql = ' AND status="{}"'.format(_status)
    data = SqlData_.search_order_list(name_sql, phone_sql, address_sql, status_sql)
    results = {'code': RET.OK, 'msg': MSG.OK}
    if not data:
        results = {"code": RET.SERVERERROR, "msg": MSG.NODATA}
        return jsonify(results)
    page_list = list()
    info = list(reversed(data))
    for i in range(0, len(info), int(limit)):
        page_list.append(info[i:i + int(limit)])
    data = page_list[int(page) - 1]
    # data = get_card_remain(data)
    results['data'] = data
    results['count'] = len(info)
    return jsonify(results)


@admin_blueprint.route('/add_product/', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        order_id = request.args.get('order_id')
        content = {'order_id': order_id}
        return render_template('add_product.html', **content)
    if request.method == 'POST':
        try:
            data = json.loads(request.form.get('data'))
            product = list(data.values())
            order_id = product[0]
            status = SqlData_.search_field('order', 'status', order_id)
            if status == '已完结':
                return jsonify({'code': RET.SERVERERROR, 'msg': '订单已完结，不可添加订单'})
            product = product[1:]
            _product_list = [product[i:i + 7] for i in range(0, len(product), 7)]
            for i in _product_list:
                product_name, position, model, color, size, quantity, price = i
                t = now_time()
                SqlData_.insert_product(product_name, position, model, color, size, quantity, price, t, '已下单', order_id)
                now_day, now_t = t.split(' ')
                info_str = "创建订单信息: " + ", ".join([product_name, position, model, color, size, quantity, price])
                SqlData_.insert_event(now_day, now_t, info_str, order_id)
            results = {"code": RET.OK, "msg": MSG.OK}
            return jsonify(results)
        except Exception as e:
            return jsonify({'code': RET.SERVERERROR, 'msg': '产品下单失败'})


@admin_blueprint.route('/order_detail/')
@login_required
def order_detail():
    order_id = request.args.get('order_id')
    content = {'order_id': order_id}
    return render_template('product_list.html', **content)


@admin_blueprint.route('/product_list/')
@login_required
def product_list():
    order_id = request.args.get('order_id')
    page = request.args.get('page')
    limit = request.args.get('limit')
    data = SqlData_.search_product(order_id)
    results = {'code': RET.OK, 'msg': MSG.OK}
    if not data:
        results['code'] = RET.SERVERERROR
        results['msg'] = MSG.NODATA
        return jsonify(results)
    page_list = list()
    info = list(reversed(data))
    for i in range(0, len(info), int(limit)):
        page_list.append(info[i:i + int(limit)])
    data = page_list[int(page) - 1]
    results['data'] = data
    results['count'] = len(info)
    return jsonify(results)


@admin_blueprint.route('/chang_product/', methods=['POST'])
@login_required
def chang_product():
    data_id = request.form.get("data_id")
    field = request.form.get("field")
    value = request.form.get("value")
    order_id = SqlData_.search_field('order_list', 'order_id', data_id)
    status = SqlData_.search_field('order', 'status', order_id)
    if status == '已完结':
        return jsonify({'code': RET.SERVERERROR, 'msg': '订单已完结，不可修改'})
    if field in ['quantity', 'price']:
        try:
            value = int(value)
        except:
            return jsonify({'code': RET.SERVERERROR, 'msg': '数量或者单价只能为整数'})
    SqlData_.update_product(field, value, data_id)
    # 添加记录
    product_name = SqlData_.search_field('order_list', 'product_name', data_id)
    t = now_time()
    now_day, now_t = t.split(' ')
    info_str = "将品名为{} 的 {} 更改为 {}".format(product_name, field, value)
    SqlData_.insert_event(now_day, now_t, info_str, order_id)
    results = {'code': RET.OK, 'msg': '更新成功'}
    return jsonify(results)


@admin_blueprint.route('/del_product/')
@login_required
def del_product():
    data_id = request.args.get('data_id')

    product_name = SqlData_.search_field('order_list', 'product_name', data_id)
    order_id = SqlData_.search_field('order_list', 'order_id', data_id)
    status = SqlData_.search_field('order', 'status', order_id)
    if status == '已完结':
        return jsonify({'code': RET.SERVERERROR, 'msg': '订单已完结，不可删除'})

    SqlData_.del_product(data_id)

    # 添加记录
    t = now_time()
    now_day, now_t = t.split(' ')
    info_str = "将品名为{} 的 订单删除".format(product_name)
    SqlData_.insert_event(now_day, now_t, info_str, order_id)
    results = {'code': RET.OK, 'msg': '删除成功'}
    return jsonify(results)


@admin_blueprint.route("/order_status/")
@login_required
def order_status():
    status = request.args.get('status')
    data_id = request.args.get('data_id')
    _status = SqlData_.search_field('order', 'status', data_id)
    if _status == '已完结':
        return jsonify({'code': RET.SERVERERROR, 'msg': '订单已完结，不可修改'})
    old_status = SqlData_.search_field('order', 'status', data_id)
    SqlData_.update_order_status(status, data_id)
    t = now_time()
    now_day, now_t = t.split(' ')
    info_str = "将订单状态 {} 更改为 {}".format(old_status, status)
    SqlData_.insert_event(now_day, now_t, info_str, data_id)
    results = {'code': RET.OK, 'msg': '更新成功'}
    return jsonify(results)


@admin_blueprint.route('/update_pay/', methods=['POST'])
@login_required
def update_pay():
    pay_num = request.form.get('pay_num')
    data_id = request.form.get('data_id')
    try:
        pay_num = abs(int(pay_num))
    except:
        return jsonify({'code': RET.SERVERERROR, 'msg': '收款金额只能为整数'})
    status = SqlData_.search_field('order', 'status', data_id)
    if status == '已完结':
        return jsonify({'code': RET.SERVERERROR, 'msg': '订单已完结，不可更新收款金额'})
    old_pay = SqlData_.search_field('order', 'pay', data_id)

    SqlData_.update_order_pay(pay_num, data_id)

    total = SqlData_.search_order_total_price(data_id)
    payed = SqlData_.search_field('order', 'pay', data_id)
    t = now_time()
    if payed >= total:
        SqlData_.update_order_status('已完结', data_id)
        SqlData_.update_order_end_time(t, data_id)

    new_pay = SqlData_.search_field('order', 'pay', data_id)

    # 添加操作记录
    now_day, now_t = t.split(' ')
    info_str = "添加收款金额: 收款前:{}, 收款金额:{}, 收款后{}".format(old_pay, pay_num, new_pay)
    SqlData_.insert_event(now_day, now_t, info_str, data_id)
    results = {'code': RET.OK, 'msg': '更新成功'}
    return jsonify(results)


@admin_blueprint.route('/receipt/')
@login_required
def receipt():
    data_id = request.args.get('data_id')
    order_info = SqlData_.search_order(data_id)
    data_id, user_name, phone, address, *ret = list(order_info)
    product_info = SqlData_.search_product(data_id)

    _product_list = list()
    for i in range(1, len(product_info) + 1):
        d = product_info[i - 1]
        d['index'] = i
        d['total'] = d['quantity'] * d['price']
        _product_list.append(d)

    now_t = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    total = SqlData_.search_order_total_price(data_id)
    content = {
        'user_name': user_name,
        'phone': phone,
        'address': address,
        'product_info': _product_list,
        'now_time': now_t,
        'total': total,
        'total_zh': formatCurrency(total)
    }
    return render_template('receipt.html', **content)


@admin_blueprint.route('/history/')
@login_required
def history():
    data_id = request.args.get('data_id')
    event_info = SqlData_.search_event(data_id)
    new_event = event_sort(event_info)
    content = {
        'event_info': new_event
    }
    return render_template('history_event.html', **content)


@admin_blueprint.route('/del_order/')
@login_required
def del_order():
    order_id = request.args.get('data_id')
    status = SqlData_.search_field('order', 'status', order_id)
    if status == '已完结':
        return jsonify({'code': RET.SERVERERROR, 'msg': '订单已完结, 不可删除'})
    SqlData_.del_order(order_id)
    results = {'code': RET.OK, 'msg': '删除成功'}
    return jsonify(results)


@admin_blueprint.route('/img_code/', methods=['GET'])
def img_code():
    try:
        code, img_str = createCodeImage()
        string = ImgCode().jiami(code)
        return jsonify({'code': RET.OK, 'data': {'string': string, 'src': img_str}})
    except Exception as e:
        return jsonify({'code': RET.SERVERERROR, 'msg': MSG.SERVERERROR})


@admin_blueprint.route('/')
def go_index():
    return redirect('/index/')
