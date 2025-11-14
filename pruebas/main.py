
from PySide6.QtWidgets import *
from PySide6.QtGui import *


app = QApplication([])

scene = QGraphicsScene()
view = QGraphicsView(scene)
view.setWindowTitle("Mapa del metro")
view.resize(1096, 1280)

mapa = QPixmap("../data/MapaMetroCDMX.png")
map_item = QGraphicsPixmapItem(mapa)
scene.addItem(map_item)

esfera = QGraphicsEllipseItem(500, 500, 30, 30)
esfera.setBrush(QBrush(QColor(0, 0, 255, 180)))
esfera.setZValue(100)
scene.addItem(esfera)

view.show()

app.exec()