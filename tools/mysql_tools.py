from tools.db_dbutils_init import get_my_connection
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s', filename="error.log")


class SqlData(object):
    def __init__(self):
        self.db = get_my_connection()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'inst'):  # 单例
            cls.inst = super(SqlData, cls).__new__(cls, *args, **kwargs)
        return cls.inst

    def connect(self):
        conn, cursor = self.db.getconn()
        return conn, cursor

    def close_connect(self, conn, cursor):
        cursor.close()
        conn.close()

    # 查询某个值在某个字段中
    def search_value_in(self, table_name, value, field):
        sql = "select * from {} where find_in_set('{}',{})".format(table_name, value, field)
        conn, cursor = self.connect()
        cursor.execute(sql)
        row = cursor.fetchone()
        self.close_connect(conn, cursor)
        if row:
            return True
        else:
            return False

    def update_user_field_int(self, field, value, user_id):
        sql = "UPDATE user_info SET {} = {} WHERE id = {}".format(field, value, user_id)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logging.error("更新用户字段" + field + "失败!" + str(e))
            conn.rollback()
        self.close_connect(conn, cursor)

    def insert_account_vice(self, v_account, v_password, c_card, top_up, refund, del_card, up_label, user_id):
        sql = "INSERT INTO vice_user(v_account, v_password, c_card, top_up, refund, del_card, up_label," \
              " user_id) VALUES ('{}','{}','{}','{}','{}','{}','{}',{})".format(v_account, v_password, c_card,
                                                                                   top_up, refund, del_card,
                                                                                   up_label, user_id)
        conn, cursor = self.connect()
        cursor.execute(sql)
        conn.commit()
        self.close_connect(conn, cursor)

    def del_vice(self, vice_id):
        sql = "DELETE FROM vice_user WHERE id = {}".format(vice_id)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logging.error("删除失败" + str(e))
            conn.rollback()
        self.close_connect(conn, cursor)

    # 一下是用户方法-----------------------------------------------------------------------------------------------------

    def insert_order(self, user_name, phone, address, now_time, status):
        sql = "INSERT INTO `order`(user_name, phone, address, start_time, status) " \
              "VALUES ('{}','{}','{}','{}','{}')".format(user_name, phone, address, now_time, status)
        conn, cursor = self.connect()
        cursor.execute(sql)
        conn.commit()
        self.close_connect(conn, cursor)

    def search_order_list(self, name_sql, phone_sql, address_sql, status_sql):
        sql = "SELECT * FROM `order` WHERE id !='' {} {} {} {}".format(name_sql, phone_sql, address_sql, status_sql)
        conn, cursor = self.connect()
        cursor.execute(sql)
        rows = cursor.fetchall()
        self.close_connect(conn, cursor)
        data = []
        for i in rows:
            data.append({
                'data_id': i[0],
                'user_name': i[1],
                'phone': i[2],
                'address': i[3],
                'start_time': str(i[4]),
                'end_time': str(i[5]) if i[5] else '暂无',
                'pay': i[6],
                'status': i[7],
                'total_price': self.search_order_total_price(i[0])
            })
        return data

    def search_order_total_price(self, order_id):
        sql = "select quantity, price from order_list where order_id={}".format(order_id)
        conn, cursor = self.connect()
        cursor.execute(sql)
        rows = cursor.fetchall()
        self.close_connect(conn, cursor)
        if rows:
            total = 0
            for row in rows:
                total += (row[0] * row[1])
            return total
        else:
            return 0

    def insert_product(self, product_name, position, model, color, size, quantity, price, now_time, status, order_id):
        sql = "INSERT INTO `order_list`(product_name, position, model, color, size, quantity, price, now_time, status, order_id) " \
              "VALUES ('{}','{}','{}','{}','{}',{},{},'{}','{}',{})".format(product_name, position, model, color, size, quantity, price, now_time, status, order_id)
        conn, cursor = self.connect()
        cursor.execute(sql)
        conn.commit()
        self.close_connect(conn, cursor)

    def search_product(self, order_id):
        sql = "SELECT * FROM `order_list` WHERE order_id={}".format(order_id)
        conn, cursor = self.connect()
        cursor.execute(sql)
        rows = cursor.fetchall()
        self.close_connect(conn, cursor)
        data = []
        for i in rows:
            data.append({
                'data_id': i[0],
                'product_name': i[1],
                'position': i[2],
                'model': i[3],
                'color': i[4],
                'size': i[5],
                'quantity': i[6],
                'price': i[7],
                'total_price': i[6] * i[7],
                'now_time': str(i[8]),
                'status': str(i[9]),
            })
        return data

    def update_product(self, field, value, data_id):
        sql = "UPDATE order_list SET {} = '{}' WHERE id = {}".format(field, value, data_id)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logging.error("更新用户字段" + field + "失败!" + str(e))
            conn.rollback()
        self.close_connect(conn, cursor)

    def del_product(self, data_id):
        sql = "DELETE FROM order_list WHERE id = {}".format(data_id)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logging.error("删除失败" + str(e))
            conn.rollback()
        self.close_connect(conn, cursor)

    def update_order_status(self, status, data_id):
        sql = "UPDATE `order` SET status = '{}' WHERE id = {}".format(status, data_id)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logging.error("更新用户字段失败!" + str(e))
            conn.rollback()
        self.close_connect(conn, cursor)

    def update_order_end_time(self, end_time, data_id):
        sql = "UPDATE `order` SET end_time = '{}' WHERE id = {}".format(end_time, data_id)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logging.error("更新用户字段失败!" + str(e))
            conn.rollback()
        self.close_connect(conn, cursor)

    def update_order_pay(self, pay_num, data_id):
        sql = "UPDATE `order` SET pay = pay + {} WHERE id = {}".format(pay_num, data_id)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logging.error("更新用户字段失败!" + str(e))
            conn.rollback()
        self.close_connect(conn, cursor)

    def search_order(self, data_id):
        sql = "SELECT * FROM `order` WHERE id={}".format(data_id)
        conn, cursor = self.connect()
        cursor.execute(sql)
        row = cursor.fetchone()
        self.close_connect(conn, cursor)
        return row

    def search_event(self, data_id):
        sql = "SELECT * FROM action_event WHERE order_id={}".format(data_id)
        conn, cursor = self.connect()
        cursor.execute(sql)
        rows = cursor.fetchall()
        self.close_connect(conn, cursor)
        data = []
        for i in rows:
            data.append({
                'now_date': str(i[1]),
                'now_time': str(i[2]),
                'event': i[3],
            })
        return data

    def insert_event(self, now_day, now_time, event, data_id):
        sql = "INSERT INTO `action_event`(now_date, now_time, event, order_id) " \
              "VALUES ('{}','{}','{}',{})".format(now_day, now_time, event, data_id)
        conn, cursor = self.connect()
        cursor.execute(sql)
        conn.commit()
        self.close_connect(conn, cursor)

    def search_field(self, table, field, order_id):
        if table == 'order':
            sql = "SELECT `{}` FROM `{}` WHERE id={}".format(field, table, order_id)
        else:
            sql = "SELECT `{}` FROM `{}` WHERE id={}".format(field, table, order_id)
        conn, cursor = self.connect()
        cursor.execute(sql)
        row = cursor.fetchone()
        self.close_connect(conn, cursor)
        return row[0]

    def del_order(self, data_id):
        sql = "DELETE FROM `order` WHERE id = {}".format(data_id)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logging.error("删除失败" + str(e))
            conn.rollback()
        self.close_connect(conn, cursor)

    def search_user_login(self, user_name):
        sql = "SELECT `account`, password, name FROM user_info WHERE BINARY account = '{}'".format(user_name)
        conn, cursor = self.connect()
        cursor.execute(sql)
        rows = cursor.fetchone()
        self.close_connect(conn, cursor)
        try:
            user_data = dict()
            user_data['account'] = rows[0]
            user_data['password'] = rows[1]
            user_data['name'] = rows[2]
            return user_data
        except:
            return {}

    def update_password(self, value, data_id):
        sql = "UPDATE user_info SET password = '{}' WHERE id = {}".format(value, data_id)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            logging.error("更新用户密码失败!" + str(e))
            conn.rollback()
        self.close_connect(conn, cursor)


SqlData_ = SqlData()


if __name__ == "__main__":
    pass
    # res = SqlData_.search_order_list()
    # print(res)
