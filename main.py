from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
import datetime
import mysql.connector

host = "37.140.192.110"
user = "u1650738_default"
password = "DN3S0bT6T3cFRYfe"
dtb = "u1650738_default"
port = 3306

today = datetime.datetime.today()
sqlToday = today.strftime("%Y-%m-%d")
today = today.strftime("%d - %m - %Y")


def show_records():
    db = mysql.connector.connect(
        host = host,
        user = user,
        passwd = password,
        db = dtb,
        port = port,
        auth_plugin='mysql_native_password'
    )
    c = db.cursor()
    c.execute("SELECT * FROM restraunts")
    records = c.fetchall()
    db.commit()
    db.close()
    return records



class RestApp(App):

    def submit(self, ins):
        self.errors = 0
        if self.nameInput.text == '':
            self.alert.text = 'Введите имя'
            self.errors += 1
        elif len(self.nameInput.text) < 3 :
            self.alert.text = 'Имя не менее 3 букв'
            self.errors += 1
        else :
            self.alert.text = ''

        if not self.time : 
            self.alert.text = 'Не выбрано время'
            self.errors += 1

        if not self.rest : 
            self.alert.text = 'Не выбран ресторан'
            self.errors += 1
        
        if self.errors >= 1 :
            self.errors = 0
        else :
            self.insertSqlTime(self.rest, self.time, self.name) 
            self.alert.color = [255 / 255, 255 / 255, 255 / 255, 1]
            self.alert.font_size = 19
            self.alert.text = f'{self.nameInput.text.title()}, Вы забронировали столик\nв ресторан {self.rest}\nна сегодня: {today}\nвремя: {self.time}'
            self.time = False


    
    def selectTime(self, ins):
        self.pressed += 1
        if self.pressed > 1 :
            self.alert.text = 'Вы уже выбрали время'
        else :
            ins.background_color = 'red'
            self.time = ins.text
            
    

    def selectRest(self, ins):
        self.alert.color = [255 / 255, 1 / 255, 1 / 255, 1]
        self.alert.font_size = 24
        self.pressed = 0
        self.alert.text = ''
        self.l.text = f'Ресторан : {ins.text}\nСегодня : {today}'
        self.rest = ins.text
        self.rightGrid.clear_widgets()
        times = self.selectSqlTime(ins.text)
        timesToList = []
        for (t,) in times :
            timesToList.append(t)
        hours = ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"]
        for h in hours :
            if h in timesToList : 
                self.rightGrid.add_widget(
                    Button(text = h, background_color = [153 / 255, 255 / 255, 153 / 255, 1], on_press = self.selectTime, disabled = True)
                )
            else :
                self.rightGrid.add_widget(
                    Button(text = h, background_color = [153 / 255, 255 / 255, 153 / 255, 1], on_press = self.selectTime, disabled = False)
                )       


    def checkSqlRow (self, rest, day) :
        db = mysql.connector.connect(
            host = host,
            user = user,
            passwd = password,
            db = dtb,
            port = port,
            auth_plugin='mysql_native_password'
        )
        c = db.cursor()
        c.execute(f"SELECT COUNT(*) FROM shedule WHERE rest='{rest}' AND date='{day}'")
        (rows,) = c.fetchone()
        return rows

    def insertSqlTime(self, rest, time, name) :
        db = mysql.connector.connect(
            host = host,
            user = user,
            passwd = password,
            db = dtb,
            port = port,
            auth_plugin='mysql_native_password'
        )
        c = db.cursor()
        q = f"INSERT INTO shedule (date, rest, time, client) VALUES ('{sqlToday}','{rest}','{time}','{name}')"
        c.execute(q)
        db.commit()
        db.close()
        return "INSERTED"
    
    def selectSqlTime (self, rest) :
        db = mysql.connector.connect(
            host = host,
            user = user,
            passwd = password,
            db = dtb,
            port = port,
            auth_plugin='mysql_native_password'
        )
        c = db.cursor()
        c.execute(f"SELECT time FROM shedule WHERE rest='{rest}' AND date='{sqlToday}'")
        times = c.fetchall()
        return times

    def build(self):
        self.timeDisabled = False
        self.rest = False
        self.time = False
        self.pressed = 0
        self.errors = 0
        self.title = "Запись в рестораны Симферополя"

        records = show_records()

        root = BoxLayout(orientation = "horizontal", padding = 3)

        left = ScrollView(size_hint = [.5,1])
        leftGrid = GridLayout(cols = 1, size_hint_y = None)
        leftGrid.bind(minimum_height = leftGrid.setter('height'))
        for (index, title) in records :
            btn = ToggleButton(
                text = title, 
                font_size ='20sp', 
                size_hint_y = None, 
                height = 100,
                group = 'records',
                background_color = [102 / 255, 102 / 255, 255 / 255 , 1],
                on_press = self.selectRest
            )
            leftGrid.add_widget(btn)

        left.add_widget(leftGrid)
        root.add_widget(left)

        right = BoxLayout(orientation = "vertical")
        self.l = Label(text='Выберите ресторан', font_size='20sp', size_hint = [1,.13], valign = 'top', halign = 'left')
        right.add_widget(self.l)
        self.rightGrid = GridLayout(cols = 4, size_hint_y = .57)
        hours = ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"]
        for h in hours : 
            self.rightGrid.add_widget(
                Button(text = h, background_color = [255 / 255, 105 / 255, 180 / 255, 1])
            )
        right.add_widget(self.rightGrid)
        self.alert = Label(text='', font_size='20sp', size_hint = [1,.23], valign = 'top', halign = 'left', color = 'red')
        right.add_widget(self.alert)
        self.nameInput = TextInput(hint_text = "Ваше имя", size_hint = [1,.13], multiline=False, font_size = 20, background_color = [1,1,1,.8])
        right.add_widget(self.nameInput)
        self.submitBtn = Button(
            text = 'Забронировать', 
            font_size = 22, 
            background_color = 'skyblue', 
            size_hint = [1,.13],
            on_press = self.submit
        )
        right.add_widget(self.submitBtn)
        root.add_widget(right)

        return root


if __name__ == "__main__":
    RestApp().run()
