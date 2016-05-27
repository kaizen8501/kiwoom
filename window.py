import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from kiwoom.kiwoom import Kiwoom
from kiwoom.kiwoom import KiwoomCallback
from kiwoom.data import Condition
from kiwoom.data import Balance
from logger import MyLogger


class ConditionItem:
    def __init__(self, the_condition):
        self.condition = the_condition

        self.combo_box_signal = QComboBox()
        self.combo_box_signal.addItems(Condition.get_signal_type_items_list())
        self.combo_box_signal.setCurrentIndex(self.combo_box_signal.findText(self.condition.신호종류))
        self.combo_box_signal.connect(self.combo_box_signal, SIGNAL("currentIndexChanged(QString)"), self.on_signal_changed)

        self.combo_box_apply = QComboBox()
        self.combo_box_apply.addItems(Condition.get_applied_items_list())
        self.combo_box_apply.setCurrentIndex(self.combo_box_apply.findText(self.condition.적용유무))
        self.combo_box_apply.connect(self.combo_box_apply, SIGNAL("currentIndexChanged(QString)"), self.on_apply_changed)

        self.button = QPushButton("조회 및 요청")
        self.button.clicked.connect(lambda: kiwoom.send_condition(self.condition))

    def on_signal_changed(self, the_신호종류):
        self.condition.신호종류 = the_신호종류

    def on_apply_changed(self, the_적용유무):
        self.condition.적용유무 = the_적용유무


class MyWindow(QMainWindow, KiwoomCallback):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('window.ui', self)
        self.ui.table_current.setHorizontalHeaderLabels(["test1", "test2", "test3"])
        self.ui.table_current.setItem(0, 0, QTableWidgetItem("test"))
        self.ui.table_current.setItem(0, 1, QTableWidgetItem("test0_1"))
        self.ui.table_current.setItem(1, 0, QTableWidgetItem("test1_0"))
        self.ui.table_current.itemChanged.connect(self.on_balance_item_changed)
        vertical_header = self.ui.table_current.verticalHeader()
        vertical_header.connect(vertical_header, SIGNAL("sectionClicked(int)"), self.on_balance_section_clicked)
        self.is_user_changing_balance = False
        self.selected_balance = []
        self.ui.combo_buy.addItems(Balance.get_available_buy_strategy())
        self.ui.combo_sell.addItems(Balance.get_available_sell_strategy())

    @pyqtSlot(str)
    def on_account_changed(self, account):
        MyLogger.instance().logger().info("account: %s", account)
        kiwoom.data.계좌번호 = account

    @pyqtSlot()
    def on_condition_refresh_btn_clicked(self):
        MyLogger.instance().logger().info("")
        kiwoom.refresh_condition_dic()

    @pyqtSlot()
    def on_balance_btn_clicked(self):
        MyLogger.instance().logger().info("")
        kiwoom.tr_balance()

    @pyqtSlot()
    def on_print_my_data_btn_clicked(self):
        MyLogger.instance().logger().info("")
        kiwoom.data.print()

    @pyqtSlot()
    def on_code_btn_clicked(self):
        MyLogger.instance().logger().info("code: %s", self.ui.edit_code.text())
        kiwoom.tr_code(self.ui.edit_code.text())

    @pyqtSlot()
    def on_code_del_btn_clicked(self):
        MyLogger.instance().logger().info("")
        for balance in self.selected_balance:
            del kiwoom.data.잔고_dic[balance.종목코드]
        self.on_data_updated(["잔고_dic"])

    @pyqtSlot()
    def on_register_real_all_btn_clicked(self):
        MyLogger.instance().logger().info("")
        잔고_dic = kiwoom.data.잔고_dic
        종목코드_list = 잔고_dic.keys()
        종목코드_list_str = ";".join(종목코드_list)
        MyLogger.instance().logger().info("종목코드_list_str %s", 종목코드_list_str)
        kiwoom.set_real_reg(종목코드_list_str)

    @pyqtSlot()
    def on_buy_strategy_add_btn_clicked(self):
        strategy_str = self.ui.combo_buy.currentText()
        MyLogger.instance().logger().info("전략: %s", strategy_str)
        for balance in self.selected_balance:
            balance.add_buy_strategy(strategy_str)
        self.on_data_updated(["잔고_dic"])

    @pyqtSlot()
    def on_sell_strategy_add_btn_clicked(self):
        strategy_str = self.ui.combo_sell.currentText()
        MyLogger.instance().logger().info("전략: %s", strategy_str)
        for balance in self.selected_balance:
            balance.add_sell_strategy(strategy_str)
        self.on_data_updated(["잔고_dic"])

    @pyqtSlot()
    def on_buy_strategy_clear_btn_clicked(self):
        MyLogger.instance().logger().info("")
        for balance in self.selected_balance:
            balance.매수전략.clear()
        self.on_data_updated(["잔고_dic"])

    @pyqtSlot()
    def on_sell_strategy_clear_btn_clicked(self):
        MyLogger.instance().logger().info("")
        for balance in self.selected_balance:
            balance.매도전략.clear()
        self.on_data_updated(["잔고_dic"])

    @pyqtSlot()
    def on_load_balance_btn_clicked(self):
        MyLogger.instance().logger().info("")
        f = open("my_list.txt", "r")
        line = f.readline()
        while line:
            str_list = line.split(";")
            종목코드 = str_list[0]
            balance = kiwoom.data.get_balance(종목코드)
            종목명 = str_list[1]
            balance.종목명 = 종목명
            목표보유수량_str = str_list[2]
            if 목표보유수량_str != "None":
                balance.목표보유수량 = int(목표보유수량_str)
            매수전략_str = str_list[3]
            매수전략_list = 매수전략_str[1:-1].split(",")
            for 매수전략_temp in 매수전략_list:
                if len(매수전략_temp) < 3:
                    continue
                매수전략 = 매수전략_temp.strip()[1:-1]  # 따옴표 제거
                balance.add_buy_strategy(매수전략)
            매도전략_str = str_list[4].strip()
            매도전략_list = 매도전략_str[1:-1].split(",")
            for 매도전략_temp in 매도전략_list:
                if len(매도전략_temp) < 3:
                    continue
                매도전략 = 매도전략_temp.strip()[1:-1]  # 따옴표 제거
                balance.add_sell_strategy(매도전략)
            line = f.readline()
        self.on_data_updated(["잔고_dic"])

    @pyqtSlot()
    def on_save_balance_btn_clicked(self):
        MyLogger.instance().logger().info("")
        f = open("my_list.txt", "w")
        for balance in kiwoom.data.잔고_dic.values():
            balance.get_str_list()
            f.write(balance.종목코드 + ";")
            f.write(balance.종목명 + ";")
            f.write(str(balance.목표보유수량) + ";")
            f.write(str(list(balance.매수전략.keys())) + ";")
            f.write(str(list(balance.매도전략.keys())) + "\n")
        f.close()

    def on_connected(self):
        self.statusBar().showMessage("Connected")

    def on_data_updated(self, key_list):
        if "계좌번호" in key_list:
            계좌번호 = kiwoom.data.계좌번호
            계좌번호_list = kiwoom.data.계좌번호_list
            self.ui.combo_account.clear()
            self.ui.combo_account.addItems(계좌번호_list)
            self.ui.combo_account.setCurrentIndex(self.ui.combo_account.findText(계좌번호))

        if "조건식_dic" in key_list:
            headers = Condition.get_table_header()
            self.ui.table_condition.setColumnCount(len(headers))
            self.ui.table_condition.setHorizontalHeaderLabels(headers)

            i = 0
            for condition in kiwoom.data.조건식_dic.values():
                condition_item = ConditionItem(condition)
                self.ui.table_condition.setItem(i, 0, QTableWidgetItem(str(condition.인덱스)))
                self.ui.table_condition.setItem(i, 1, QTableWidgetItem(condition.조건명))
                self.ui.table_condition.setCellWidget(i, 2, condition_item.combo_box_signal)
                self.ui.table_condition.setCellWidget(i, 3, condition_item.combo_box_apply)
                self.ui.table_condition.setCellWidget(i, 4, condition_item.button)
                i += 1
            kiwoom.data.print()

        if "잔고_dic" in key_list:
            self.is_user_changing_balance = False
            headers = Balance.get_table_header()
            self.ui.table_current.clear()
            self.ui.table_current.setColumnCount(len(headers))
            self.ui.table_current.setHorizontalHeaderLabels(headers)
            self.ui.table_current.setRowCount(len(kiwoom.data.잔고_dic))
            #self.selected_balance.clear()
            #self.ui.txt_balance.clear()

            i = 0
            for balance in kiwoom.data.잔고_dic.values():
                str_list = balance.get_str_list()
                for j in range(0, len(str_list)):
                    self.ui.table_current.setItem(i, j, QTableWidgetItem(str(str_list[j])))
                i += 1

            self.is_user_changing_balance = True
            kiwoom.data.print()

    def on_balance_item_changed(self, item):
        if not self.is_user_changing_balance:
            return
        row = item.row()
        col = item.column()
        value = item.text()
        MyLogger.instance().logger().info("row:%d, col:%d, val:%s", row, col, value)

        종목코드_item = self.ui.table_current.item(row, 0)
        종목코드 = 종목코드_item.text()
        balance = kiwoom.data.get_balance(종목코드)
        changed_key = Balance.get_table_header()[col]
        if changed_key == "목표보유수량":
            balance.목표보유수량 = int(value)
        else:
            return

    def on_balance_section_clicked(self, row):
        MyLogger.instance().logger().info("row: %d", row)
        rows = []
        for idx in self.ui.table_current.selectedIndexes():
            current_row = idx.row()
            if current_row not in rows:
                rows.append(current_row)

        self.selected_balance.clear()
        for row in rows:
            종목코드_item = self.ui.table_current.item(row, 0)
            if not 종목코드_item:  # 빈칸(None)인 경우
                continue
            종목코드 = 종목코드_item.text()
            balance = kiwoom.data.get_balance(종목코드)
            self.selected_balance.append(balance)

        종목명_list = []
        for balance in self.selected_balance:
            종목명_list.append(balance.종목명)
        selected_balance_str = ",".join(종목명_list)
        self.ui.txt_balance.setText(selected_balance_str)

if __name__ == "__main__":
    MyLogger.instance().logger().info("\n\n============================ start application =====================")
    app = QApplication(sys.argv)
    window = MyWindow()
    kiwoom = Kiwoom.instance()
    kiwoom.set_callback(window)
    window.show()
    app.exec_()
