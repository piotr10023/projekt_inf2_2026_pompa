import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF 
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath


class Krany(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 220)
        self.setMaximumSize(200, 220)


        # Parametry geometryczne
        self.top_trapez_h = 30
        self.rect_h = 100
        self.bot_trapez_h = 30

        self.width_top = 100
        self.width_mid = 70
        self.width_bot = 20

        self.total_tank_height = self.top_trapez_h + self.rect_h + self.bot_trapez_h

        self._poziom = 0.5

        self.draw_x = 50
        self.draw_y = 50

    def setPoziom(self, poziom):
        self._poziom = max(0.0, min(1.0, poziom))
        self.update()

    def setPolozenie(self, x, y):
        self.draw_x = x
        self.draw_y = y
        self.update()

    def getPoziom(self):
        return self._poziom

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx = self.draw_x + (self.width_top / 2)
        start_y = self.draw_y

        # kształt zbiornika
        path = QPainterPath()

        p1_tl = QPointF(cx - self.width_top / 2, start_y)
        p1_tr = QPointF(cx + self.width_top / 2, start_y)
        p2_ml = QPointF(cx - self.width_mid / 2, start_y + self.top_trapez_h)
        p2_mr = QPointF(cx + self.width_mid / 2, start_y + self.top_trapez_h)
        p3_bl = QPointF(cx - self.width_mid / 2, start_y + self.top_trapez_h + self.rect_h)
        p3_br = QPointF(cx + self.width_mid / 2, start_y + self.top_trapez_h + self.rect_h)
        p4_bl = QPointF(cx - self.width_bot / 2, start_y + self.total_tank_height)
        p4_br = QPointF(cx + self.width_bot / 2, start_y + self.total_tank_height)

        path.moveTo(p1_tl)
        path.lineTo(p1_tr)
        path.lineTo(p2_mr)
        path.lineTo(p3_br)
        path.lineTo(p4_br)
        path.lineTo(p4_bl)
        path.lineTo(p3_bl)
        path.lineTo(p2_ml)
        path.lineTo(p1_tl)
        path.closeSubpath()

        # ciecz
        painter.save()
        painter.setClipPath(path)

        liquid_height_px = self.total_tank_height * self._poziom
        rect_liquid = QRectF(
            cx - self.width_top / 2,
            start_y + self.total_tank_height - liquid_height_px,
            self.width_top,
            liquid_height_px,
        )
        painter.fillRect(rect_liquid, QColor(0, 120, 255, 180))
        painter.restore()

        # obrys
        pen = QPen(Qt.gray, 4)
        painter.setPen(pen)
        painter.drawPath(path)
        
        

    

class Rura:
    def __init__(self, punkty, grubosc=12, kolor=Qt.gray):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.kolor_cieczy = QColor(0, 180, 255)
        self.czy_plynie = False

    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    def draw(self, painter):
        if len(self.punkty) < 2:
            return

        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        
        pen_rura = QPen(self.kolor_rury, self.grubosc,
                        Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

       
        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 4,
                             Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)

class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pusty(self):
        return self.aktualna_ilosc <= 0.1

    def czy_pelny(self):
        return self.aktualna_ilosc >= self.pojemnosc - 0.1

    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)

    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)

    def draw(self, painter):
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.drawRect(
                int(self.x + 3),
                int(y_start),
                int(self.width - 6),
                int(h_cieczy - 2)
            )

        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height)
        )

        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)

    
    def napelnij_do_pelna(self):
        self.aktualna_ilosc = self.pojemnosc
        self.aktualizuj_poziom()

    def oproznij(self):
        self.aktualna_ilosc = 0.0
        self.aktualizuj_poziom()


class pompa:
    def __init__(self, x, y, width=50, height=70, nazwa=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa
        self.pojemnosc = 100.0
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0

    def dodaj_ciecz(self, ilosc):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        self.aktualna_ilosc += dodano
        self.aktualizuj_poziom()
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.aktualizuj_poziom()
        return usunieto

    def aktualizuj_poziom(self):
        self.poziom = self.aktualna_ilosc / self.pojemnosc

    def czy_pusty(self):
        return self.aktualna_ilosc <= 0.1

    def czy_pelny(self):
        return self.aktualna_ilosc >= self.pojemnosc - 0.1

    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)

    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)

    def draw(self, painter):
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.drawRect(
                int(self.x + 3),
                int(y_start),
                int(self.width - 6),
                int(h_cieczy - 2)
            )

        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height)
        )

        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)

    
    def napelnij_do_pelna(self):
        self.aktualna_ilosc = self.pojemnosc
        self.aktualizuj_poziom()

    def oproznij(self):
        self.aktualna_ilosc = 0.0
        self.aktualizuj_poziom()

class ScenaInstalacji(QWidget):
    def __init__(self, pompa,grzalka, zbiornik_koncowy, rura_lewa, rura_prawa, rura_pompa_grzalka, rura_grzalka_zbiornik, parent=None):
        super().__init__(parent)
        self.pompa = pompa
        self.grzalka = grzalka
        self.zbiornik_koncowy = zbiornik_koncowy
        self.rura_lewa = rura_lewa
        self.rura_prawa = rura_prawa
        self.rura_pompa_grzalka = rura_pompa_grzalka
        self.rura_grzalka_zbiornik = rura_grzalka_zbiornik
        self.setMinimumSize(1200, 400)
        self.setStyleSheet("background-color: #222;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.rura_lewa.draw(painter)
        self.rura_prawa.draw(painter)
        self.pompa.draw(painter)
        self.rura_pompa_grzalka.draw(painter)
        self.grzalka.draw(painter)
        self.rura_grzalka_zbiornik.draw(painter)
        self.zbiornik_koncowy.draw(painter)
       


        self.pompa.draw(painter)



class Grzalka:
    def __init__(self, x, y, width=50, height=70, nazwa="GRZAŁKA"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.nazwa = nazwa

        self.temperatura = 20.0   # °C
        self.wlaczona = False

    def wlacz(self):
        self.wlaczona = True

    def wylacz(self):
        self.wlaczona = False

    def krok(self):
        if self.wlaczona:
            self.temperatura = min(self.temperatura + 0.3, 90)
        else:
            self.temperatura = max(self.temperatura - 0.1, 20)

    def kolor_cieczy(self):
        t = (self.temperatura - 20) / 70
        r = int(255 * t)
        b = int(255 * (1 - t))
        return QColor(r, 50, b)

    def draw(self, painter):
        # ciecz
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.kolor_cieczy())
        painter.drawRect(
            int(self.x + 5),
            int(self.y + 5),
            int(self.width - 10),
            int(self.height - 10)
        )

        pen = QPen(Qt.black, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.x, self.y, self.width, self.height)

        painter.drawText(self.x, self.y - 5, self.nazwa)
        painter.drawText(self.x, self.y + self.height + 15,
                         f"{int(self.temperatura)} °C")





class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laboratorium: Zbiornik PyQt")
        self.resize(1500, 900)
        uklad_pionowy_calosc = QVBoxLayout()

        from PyQt5.QtCore import QTimer

        self.timer = QTimer()
        self.timer.timeout.connect(self.krok_symulacji)

        


        self.running = False
        self.predkosc_opadania = 0.005  

        from PyQt5.QtWidgets import QPushButton
        self.btn_start = QPushButton("START")
        self.btn_start.clicked.connect(self.start_stop)
        uklad_pionowy_calosc.addWidget(self.btn_start)
        
        uklad_kranow = QHBoxLayout()

        lewy_uklad = QVBoxLayout()

        # --- kran 1 ---
        self.slider1 = QSlider(Qt.Orientation.Horizontal) 
        self.slider1.setRange(0, 100)
        self.slider1.setValue(50)
        self.slider1.valueChanged.connect(self.zmien_poziom1)
        lewy_uklad.addWidget(self.slider1) 

        self.label1 = QLabel("Poziom: 50%")
        self.label1.setAlignment(Qt.AlignCenter)
        lewy_uklad.addWidget(self.label1)

        self.krany1 = Krany()
        self.krany1.setStyleSheet("background-color: #222;")
        lewy_uklad.addWidget(self.krany1)
        uklad_kranow.addLayout(lewy_uklad)


        prawy_uklad = QVBoxLayout()
       

        # --- kran 2 ---
        self.slider2 = QSlider(Qt.Horizontal)
        self.slider2.setRange(0, 100)
        self.slider2.setValue(50)
        self.slider2.valueChanged.connect(self.zmien_poziom2)
        prawy_uklad.addWidget(self.slider2)

        self.label2 = QLabel("Poziom: 50%")
        self.label2.setAlignment(Qt.AlignCenter)
        prawy_uklad.addWidget(self.label2)
        self.krany2 = Krany()
        self.krany2.setStyleSheet("background-color: #222;")
        prawy_uklad.addWidget(self.krany2)
        uklad_kranow.addLayout(prawy_uklad)

        uklad_pionowy_calosc.addLayout(uklad_kranow)
        
        # --- RURY ---
        self.rura_lewa = Rura([
            (100, 0),   
            (100, 50),
            (460, 50),
            (460, 60)    
        ])

        self.rura_prawa = Rura([
            (840, 0),   
            (840, 50),
            (490, 50),
            (490, 60)
        ])
        

        self.pompa = pompa(450, 50, width=50, height=70, nazwa="POMPA")
        self.pompa.aktualna_ilosc = 0.0
        self.pompa.aktualizuj_poziom()
        print(self.pompa.aktualna_ilosc)
        
        

        self.grzalka = Grzalka(450,180 )

        self.rura_pompa_grzalka = Rura([
            (475, 120),   
            (475, 180),])

        self.zbiornik_koncowy = Zbiornik(
            x=440,
            y=300,
            width=70,
            height=90,
            nazwa="grzejnik"
        )

        self.rura_grzalka_zbiornik = Rura([
            (475, 250),
            (475, 300)
        ])


           
        self.scena = ScenaInstalacji(self.pompa, self.grzalka, self.zbiornik_koncowy,self.rura_lewa, self.rura_prawa, self.rura_pompa_grzalka, self.rura_grzalka_zbiornik)
            
        uklad_pionowy_calosc.addWidget(self.scena) 


        




        self.setLayout(uklad_pionowy_calosc) 
        

        






        

        

    def zmien_poziom1(self, value):
        poziom_float = value / 100.0
        self.krany1.setPoziom(poziom_float)
        self.label1.setText(f"Poziom: {value}%")

    def zmien_poziom2(self, value):
        poziom_float = value / 100.0
        self.krany2.setPoziom(poziom_float)
        self.label2.setText(f"Poziom: {value}%")

    def start_stop(self):
        if self.running:
            self.timer.stop()
            self.btn_start.setText("START")
        else:
            self.timer.start(50)
            self.btn_start.setText("STOP")

        self.running = not self.running

    
    
    def krok_symulacji(self):
        if not self.running:
            return

    # Kran 1 → pompa
        p1 = self.krany1.getPoziom()
        if p1 > 0:
            ubytek = min(self.predkosc_opadania, p1)
            self.krany1.setPoziom(p1 - ubytek)
            self.pompa.dodaj_ciecz(ubytek * 100)
            self.rura_lewa.ustaw_przeplyw(True)
        else:
            self.rura_lewa.ustaw_przeplyw(False)

    # Kran 2 → pompa
        p2 = self.krany2.getPoziom()
        if p2 > 0:
            ubytek = min(self.predkosc_opadania, p2)
            self.krany2.setPoziom(p2 - ubytek)
            self.pompa.dodaj_ciecz(ubytek * 100)
            self.rura_prawa.ustaw_przeplyw(True)
        else:
            self.rura_prawa.ustaw_przeplyw(False)
        # pompa -> grzałka
        if self.pompa.aktualna_ilosc > 1:
            self.grzalka.wlacz()
            wydajnosc = 0.3
            self.pompa.usun_ciecz(wydajnosc)
            self.rura_pompa_grzalka.ustaw_przeplyw(True)
        else:
            self.grzalka.wylacz()
            self.rura_pompa_grzalka.ustaw_przeplyw(False)

        self.grzalka.krok()
        # grzałka -> zbiornik końcowy
        if self.pompa.aktualna_ilosc > 0.3:
            ilosc = self.pompa.usun_ciecz(0.3)
            self.zbiornik_koncowy.dodaj_ciecz(ilosc)
            self.rura_grzalka_zbiornik.ustaw_przeplyw(True)
        else:
            self.rura_grzalka_zbiornik.ustaw_przeplyw(False)

        self.scena.update()








    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())