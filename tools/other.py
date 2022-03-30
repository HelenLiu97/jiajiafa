import datetime
from functools import wraps

from flask import session, redirect, g


def now_time():
    now_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return now_datetime


def formatCurrency(currencyDigits):
    '''本函数旨在将数字化的金额（不含千分符）转化为中文的大写金额'''
    maximum_number = 99999999999.99
    cn_zero = "零"
    cn_one = "壹"
    cn_two = "贰"
    cn_three = "叁"
    cn_four = "肆"
    cn_five = "伍"
    cn_six = "陆"
    cn_seven = "柒"
    cn_eight = "捌"
    cn_nine = "玖"
    cn_ten = "拾"
    cn_hundred = "佰"
    cn_thousand = "仟"
    cn_ten_thousand = "万"
    cn_hundred_million = "亿"
    cn_symbol = "人民币"
    cn_dollar = "元"
    cn_ten_cent = "角"
    cn_cent = "分"
    cn_integer = "整"
    integral = None
    decimal = None
    outputCharacters = None
    parts = None
    digits, radices, bigRadices, decimals = None, None, None, None
    zeroCount = None
    i, p, d = None, None, None
    quotient, modulus = None, None
    currencyDigits = str(currencyDigits)
    if currencyDigits == "":
        return ""
    if float(currencyDigits) > maximum_number:
        print("转换金额过大!")
        return ""
    parts = currencyDigits.split(".")
    if len(parts) > 1:
        integral = parts[0]
        decimal = parts[1]
        decimal = decimal[0:2]
        if decimal == "0" or decimal == "00":
            decimal = ""
    else:
        integral = parts[0]
        decimal = ""
    digits = [cn_zero, cn_one, cn_two, cn_three, cn_four, cn_five, cn_six, cn_seven, cn_eight, cn_nine]
    radices = ["", cn_ten, cn_hundred, cn_thousand]
    bigRadices = ["", cn_ten_thousand, cn_hundred_million]
    decimals = [cn_ten_cent, cn_cent]
    outputCharacters = ""
    if int(integral) > 0:
        zeroCount = 0
        for i in range(len(integral)):
            p = len(integral) - i - 1
            d = integral[i]
            quotient = int(p / 4)
            modulus = p % 4
            if d == "0":
                zeroCount += 1
            else:
                if zeroCount > 0:
                    outputCharacters += digits[0]
                zeroCount = 0
                outputCharacters = outputCharacters + digits[int(d)] + radices[modulus]
            if modulus == 0 and zeroCount < 4:
                outputCharacters = outputCharacters + bigRadices[quotient]
        outputCharacters += cn_dollar
    if decimal != "":
        jiao = decimal[0]
        if jiao == "":
            jiao = "0"
        try:
            fen = decimal[1]
        except:
            fen = "0"
        if fen == "":
            fen = "0"
        if jiao == "0" and fen == "0":
            pass
        if jiao == "0" and fen != "0":
            outputCharacters = outputCharacters + cn_zero + digits[int(fen)] + decimals[1]
        if jiao != "0" and fen == "0":
            outputCharacters = outputCharacters + digits[int(jiao)] + decimals[0]
        if jiao != "0" and fen != "0":
            outputCharacters = outputCharacters + digits[int(jiao)] + decimals[0]
            outputCharacters = outputCharacters + digits[int(fen)] + decimals[1]
    if outputCharacters == "":
        outputCharacters = cn_zero + cn_dollar
    if decimal == "":
        outputCharacters = outputCharacters + cn_integer
    outputCharacters = outputCharacters
    return outputCharacters


def Reverse(lst):
    return [ele for ele in reversed(lst)]


def event_sort(event_list):
    event_list = Reverse(event_list)
    now_date = list()

    for event in event_list:
        if event.get('now_date') not in now_date:
            now_date.append(event.get('now_date'))

    info_dict = dict()
    for now_d in now_date:
        _list = list()
        for event in event_list:
            if now_d == event.get('now_date'):
                _list.append(event)
        info_dict[now_d] = _list

    return info_dict


def login_required(view_func):
    """自定义装饰器判断用户是否登录
    使用装饰器装饰函数时，会修改被装饰的函数的__name属性和被装饰的函数的说明文档
    为了不让装饰器影响被装饰的函数的默认的数据，我们会使用@wraps装饰器，提前对view_funcJ进行装饰
    """

    @wraps(view_func)
    def wraaper(*args, **kwargs):
        try:
            """具体实现判断用户是否登录的逻辑"""
            user_name = session.get('name')
            if not user_name:
                return redirect('/login/')
            else:
                # 当用户已登录，使用g变量记录用户的user_id，方便被装饰是的视图函数中可以直接使用
                g.user_name = user_name
                # 执行被装饰的视图函数
                return view_func(*args, **kwargs)
        except:
            return redirect('/login/')

    return wraaper
