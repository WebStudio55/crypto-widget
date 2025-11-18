# crypto_widget_modern_slide_preloaded.py
import sys
import os
import json
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QSpinBox,
    QLineEdit, QSlider, QMenu, QDialog, QLabel, QHBoxLayout, QCheckBox,
    QGridLayout, QFrame, QSizePolicy, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QFont, QColor, QPainter, QFontMetrics, QPixmap, QAction
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal, QThread
import requests
import ctypes

# ---------- Config ----------
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), "crypto_widget_settings.json")
ICON_CACHE_DIR = os.path.join(os.path.expanduser("~"), "crypto_widget_icons")
os.makedirs(ICON_CACHE_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    "symbol1": "BTCUSDT",
    "symbol2": "ETHUSDT",
    "symbol3": "SOLUSDT",
    "decimals1": 2,
    "decimals2": 2,
    "decimals3": 2,
    "text_size": 24,
    "bg_opacity": 0.7,
    "update_interval": 10,
    "cycle_interval": 3,
    "cycle_enabled": True,
    "pos_x": 200,
    "pos_y": 200
}
config = DEFAULT_CONFIG.copy()

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                loaded = json.load(f)
                config.update(loaded)
        except Exception:
            pass

def save_settings():
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception:
        pass

# ---------- Icon & Price Utilities ----------
def make_fallback_pixmap(symbol_upper: str, size: int = 128) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(60, 60, 60))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(0, 0, size, size)
    letter = symbol_upper[:1].upper() if symbol_upper else "?"
    font = QFont("Arial", max(10, size // 2), QFont.Weight.Bold)
    p.setFont(font)
    p.setPen(QColor(255, 255, 255))
    fm = QFontMetrics(font)
    tw = fm.horizontalAdvance(letter)
    th = fm.ascent()
    p.drawText((size - tw) // 2, (size + th) // 2, letter)
    p.end()
    return pix

def icon_cache_path(symbol: str) -> str:
    symbol_upper = symbol.replace("USDT", "").upper()
    return os.path.join(ICON_CACHE_DIR, f"{symbol_upper}.png")

def clear_icon_cache():
    try:
        for fname in os.listdir(ICON_CACHE_DIR):
            path = os.path.join(ICON_CACHE_DIR, fname)
            try:
                os.remove(path)
            except Exception:
                pass
    except Exception:
        pass

# ---------- Background Workers ----------
class PriceWorker(QThread):
    price_fetched = pyqtSignal(str, object)
    def __init__(self, symbol: str, parent=None):
        super().__init__(parent)
        self.symbol = symbol
    def run(self):
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={self.symbol.upper()}"
            r = requests.get(url, timeout=6)
            r.raise_for_status()
            price = float(r.json().get("price", 0.0))
            self.price_fetched.emit(self.symbol, price)
        except Exception:
            self.price_fetched.emit(self.symbol, None)

class IconWorker(QThread):
    icon_fetched = pyqtSignal(str, QPixmap)
    def __init__(self, symbol: str, parent=None):
        super().__init__(parent)
        self.symbol = symbol
    def run(self):
        symbol_upper = self.symbol.replace("USDT", "").upper()
        cache_file = icon_cache_path(self.symbol)
        if os.path.exists(cache_file):
            pix = QPixmap(cache_file)
            if not pix.isNull():
                self.icon_fetched.emit(self.symbol, pix)
                return
        try:
            url = f"https://bin.bnbstatic.com/static/assets/logos/{symbol_upper}.png"
            r = requests.get(url, timeout=8)
            r.raise_for_status()
            data = r.content
            try:
                with open(cache_file, "wb") as fh:
                    fh.write(data)
            except Exception:
                pass
            pix = QPixmap()
            if pix.loadFromData(data):
                self.icon_fetched.emit(self.symbol, pix)
                return
        except Exception:
            pass
        pix = make_fallback_pixmap(symbol_upper, size=128)
        self.icon_fetched.emit(self.symbol, pix)

# ---------- Settings Dialog ----------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crypto Widget Settings")
        self.setModal(True)
        self.setWindowOpacity(0.0)
        self.setMinimumWidth(360)
        self._drag_pos = None
        self._build_ui()
        self._apply_styles()
        self._load_config_values()
        self._setup_shadow()
        self._fade_in()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.settingsContent = QFrame()
        self.settingsContent.setObjectName("settingsContent")
        content_layout = QVBoxLayout(self.settingsContent)
        layout.addWidget(self.settingsContent)

        grid = QGridLayout()
        grid.setVerticalSpacing(10)
        grid.setHorizontalSpacing(10)

        self.symbol1_edit = QLineEdit()
        self.decimals1_spin = QSpinBox(); self.decimals1_spin.setRange(0,8)
        self.symbol2_edit = QLineEdit()
        self.decimals2_spin = QSpinBox(); self.decimals2_spin.setRange(0,8)
        self.symbol3_edit = QLineEdit()
        self.decimals3_spin = QSpinBox(); self.decimals3_spin.setRange(0,8)

        grid.addWidget(QLabel("Coin 1"),1,0); grid.addWidget(self.symbol1_edit,1,1)
        grid.addWidget(self.decimals1_spin,1,2)
        grid.addWidget(QLabel("Coin 2"),2,0); grid.addWidget(self.symbol2_edit,2,1)
        grid.addWidget(self.decimals2_spin,2,2)
        grid.addWidget(QLabel("Coin 3"),3,0); grid.addWidget(self.symbol3_edit,3,1)
        grid.addWidget(self.decimals3_spin,3,2)
        content_layout.addLayout(grid)

        # sliders
        self.text_size_label = QLabel(); self.text_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.text_size_slider.setRange(8,64)
        self.text_size_slider.valueChanged.connect(lambda val: self.text_size_label.setText(f"Text Size: {val}px"))

        self.bg_label = QLabel(); self.bg_slider = QSlider(Qt.Orientation.Horizontal)
        self.bg_slider.setRange(0,100)
        self.bg_slider.valueChanged.connect(lambda val: self.bg_label.setText(f"Background Opacity: {val}%"))

        self.cycle_label = QLabel(); self.cycle_slider = QSlider(Qt.Orientation.Horizontal)
        self.cycle_slider.setRange(1,60)
        self.cycle_slider.valueChanged.connect(lambda val: self.cycle_label.setText(f"Cycle Interval: {val}s"))
        
        self.update_label = QLabel(); self.update_slider = QSlider(Qt.Orientation.Horizontal)
        self.update_slider.setRange(1, 300)
        self.update_slider.valueChanged.connect(lambda val: self.update_label.setText(f"Update Interval: {val}s"))

        content_layout.addWidget(self.text_size_label)
        content_layout.addWidget(self.text_size_slider)
        content_layout.addWidget(self.bg_label)
        content_layout.addWidget(self.bg_slider)
        content_layout.addWidget(self.cycle_label)
        content_layout.addWidget(self.cycle_slider)
        content_layout.addWidget(self.update_label)
        content_layout.addWidget(self.update_slider)

        # checkboxes
        self.cycle_checkbox = QCheckBox("Enable Symbol Rotation")
        content_layout.addWidget(self.cycle_checkbox)

        # buttons
        btn_row = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Icon Cache"); refresh_btn.clicked.connect(self._on_refresh_cache)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn = QPushButton("Save"); save_btn.clicked.connect(self._on_save)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn = QPushButton("Cancel"); cancel_btn.clicked.connect(self._fade_close)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(refresh_btn); btn_row.addStretch(); btn_row.addWidget(cancel_btn); btn_row.addWidget(save_btn)
        content_layout.addLayout(btn_row)

    def _apply_styles(self):
        self.setStyleSheet("""
        QDialog { background: white; }
        #settingsContent {
            background: #f6f7f8;
            color: #333;
            border-radius: 12px;
            padding: 12px;
        }
        QLabel { color: #333; font-weight: 500; }
        QSpinBox { width: 30px; }
        QLineEdit { min-width: 120px; }
        QSpinBox::up-button, QSpinBox::down-button {  }
        QSpinBox::up-arrow, QSpinBox::down-arrow { color: #ddd; }
        QLineEdit, QSpinBox { background: #fff; color: #333; border-radius: 3px; padding: 4px; border: 1px solid #c7c7c7; }
        QSlider { background: rgba(255,255,255,0.1); color: #333; border-radius: 3px; padding: 4px; }
        QPushButton { padding: 6px 14px; border-radius: 3px; background: #e5e5e5; color: #333; border: 1px solid #c7c7c7; }
        QPushButton:hover { background: #3a83f5; color: #fff; border-color: #0d59d3; }
        """)

    def _setup_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0); shadow.setYOffset(5)
        shadow.setColor(QColor(0,0,0,120))
        self.setGraphicsEffect(shadow)

    def _load_config_values(self):
        self.symbol1_edit.setText(config["symbol1"])
        self.symbol2_edit.setText(config["symbol2"])
        self.symbol3_edit.setText(config["symbol3"])
        self.decimals1_spin.setValue(config["decimals1"])
        self.decimals2_spin.setValue(config["decimals2"])
        self.decimals3_spin.setValue(config["decimals3"])
        self.text_size_slider.setValue(config["text_size"])
        self.bg_slider.setValue(int(config["bg_opacity"]*100))
        self.cycle_slider.setValue(config["cycle_interval"])
        self.cycle_checkbox.setChecked(bool(config.get("cycle_enabled",True)))
        self.update_slider.setValue(config.get("update_interval",10))
        self.update_label.setText(f"Update Interval: {self.update_slider.value()}s")

    # --- animations ---
    def _fade_in(self):
        self.setWindowOpacity(1.0)

    def _fade_close(self):
        self.close()

    # --- buttons ---
    def _on_refresh_cache(self):
        clear_icon_cache()
        parent = self.parent()
        if parent and hasattr(parent, "reload_icons_async"):
            parent.reload_icons_async()
        QMessageBox.information(self, "Cache Cleared", "Icon cache cleared. Icons will be re-downloaded.")

    def _on_save(self):
        config["symbol1"] = self.symbol1_edit.text().strip().upper() or DEFAULT_CONFIG["symbol1"]
        config["symbol2"] = self.symbol2_edit.text().strip().upper() or DEFAULT_CONFIG["symbol2"]
        config["symbol3"] = self.symbol3_edit.text().strip().upper() or DEFAULT_CONFIG["symbol3"]
        config["decimals1"] = int(self.decimals1_spin.value())
        config["decimals2"] = int(self.decimals2_spin.value())
        config["decimals3"] = int(self.decimals3_spin.value())
        config["text_size"] = int(self.text_size_slider.value())
        config["bg_opacity"] = float(self.bg_slider.value())/100.0
        config["cycle_interval"] = int(self.cycle_slider.value())
        config["cycle_enabled"] = bool(self.cycle_checkbox.isChecked())
        config["update_interval"] = int(self.update_slider.value())
        save_settings()
        parent = self.parent()
        if parent and hasattr(parent, "apply_settings"):
            parent.apply_settings()
        self._fade_close()

# ---------- Main Widget ----------
class CryptoWidget(QWidget):
    PADDING = 10
    SLIDE_SPEED = 12  # pixels per frame
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint |
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.move(config.get("pos_x",200), config.get("pos_y",200))

        # Force above taskbar on Windows
        if sys.platform=="win32":
            hwnd = self.winId().__int__()
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0,0,0,0, 0x13)

        # Symbols & prices
        self.symbols = [config["symbol1"], config["symbol2"], config["symbol3"]]
        self.decimals = [config["decimals1"], config["decimals2"], config["decimals3"]]

        self.current_index = 0
        self.slide_offset = 0
        self.slide_in_progress = False

        # Preload slides data: icon + symbol + price
        self.slides = {}
        for s in self.symbols:
            self.slides[s] = {
                "icon": make_fallback_pixmap(s.replace("USDT",""),size=128),
                "symbol": s.replace("USDT",""),
                "price": None
            }

        # timers
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_prices)
        self.update_timer.start(max(5,config.get("update_interval",30))*1000)

        self.cycle_timer = QTimer(self)
        self.cycle_timer.timeout.connect(self.start_slide)
        if config.get("cycle_enabled",True):
            self.cycle_timer.start(max(3,config.get("cycle_interval",3))*1000)

        self.slide_timer = QTimer(self)
        self.slide_timer.timeout.connect(self._slide_step)

        self.setMinimumSize(200,80)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.Fixed)

        # Load icons and initial prices
        self.reload_icons_async()
        self.update_prices()
        self.show()

    # --- price & icons ---
    def update_prices(self):
        for s in self.symbols:
            worker = PriceWorker(s,parent=self)
            worker.price_fetched.connect(self._on_price_fetched)
            worker.finished.connect(worker.deleteLater)
            worker.start()

    def _on_price_fetched(self, symbol, price):
        if symbol in self.slides:
            self.slides[symbol]["price"] = price
            if symbol == self.symbols[self.current_index]:
                self._resize_to_content()
                self.update()

    def reload_icons_async(self):
        for s in self.symbols:
            w = IconWorker(s,parent=self)
            w.icon_fetched.connect(self._on_icon_fetched)
            w.finished.connect(w.deleteLater)
            w.start()

    def _on_icon_fetched(self, symbol, pixmap):
        if symbol in self.slides:
            self.slides[symbol]["icon"] = pixmap
            if symbol == self.symbols[self.current_index]:
                self._resize_to_content()
                self.update()

    # --- slide animation ---
    def start_slide(self):
        if not config.get("cycle_enabled", True) or self.slide_in_progress:
            return
        self.prev_index = self.current_index
        self.current_index = (self.current_index + 1) % len(self.symbols)
        self.slide_offset = self.width()
        self.slide_in_progress = True
        self.slide_timer.start(30)

    def _slide_step(self):
        self.slide_offset -= self.SLIDE_SPEED
        if self.slide_offset <= 0:
            self.slide_offset = 0
            self.slide_in_progress = False
            self.slide_timer.stop()
        self.update()

    # --- painting ---
    def _resize_to_content(self):
        font=QFont("Arial",config.get("text_size",24))
        fm=QFontMetrics(font)
        slide = self.slides[self.symbols[self.current_index]]
        price_text = f"{slide['price']:.{self.decimals[self.current_index]}f}" if slide["price"] is not None else "0000.00"
        symbol_width=fm.horizontalAdvance(slide["symbol"])
        price_width=fm.horizontalAdvance(price_text)
        icon_size=int(config.get("text_size",24)*1.7)
        total_width=symbol_width+price_width+icon_size+self.PADDING*3
        total_height=max(fm.height(),icon_size)+self.PADDING*2
        self.setMinimumSize(total_width,total_height)
        self.resize(total_width,total_height)

    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect=self.rect()
        bg_alpha=int(config.get("bg_opacity",0.7)*255)
        bg_color=QColor(0,0,0,bg_alpha)
        painter.setBrush(bg_color)
        painter.setPen(QColor(50,50,50,max(80,bg_alpha)))
        painter.drawRoundedRect(rect.adjusted(0,0,-1,-1),5,5)
        font=QFont("Calibri",config.get("text_size",24))
        painter.setFont(font)
        fm=QFontMetrics(font)
        y_pos=self.height()//2+fm.ascent()//3

        # previous slide
        if self.slide_in_progress:
            prev_slide = self.slides[self.symbols[self.prev_index]]
            offset = self.slide_offset - self.width()
            x = int(self.PADDING + offset)
            painter.setPen(QColor(255,255,255,200))
            icon_size=int(config.get("text_size",24)*1.7)
            painter.drawPixmap(x,int((self.height()-icon_size)//2),icon_size,icon_size,prev_slide["icon"])
            x += icon_size + self.PADDING
            painter.drawText(x,y_pos,prev_slide["symbol"])
            x += fm.horizontalAdvance(prev_slide["symbol"]) + self.PADDING
            price_text = f"{prev_slide['price']:.{self.decimals[self.prev_index]}f}" if prev_slide["price"] is not None else "..."
            painter.drawText(x,y_pos,price_text)

        # current slide
        slide = self.slides[self.symbols[self.current_index]]
        offset = self.slide_offset
        x = int(self.PADDING + offset)
        painter.setPen(QColor(255,255,255,255))
        icon_size=int(config.get("text_size",24)*1.7)
        painter.drawPixmap(x,int((self.height()-icon_size)//2),icon_size,icon_size,slide["icon"])
        x += icon_size + self.PADDING
        painter.drawText(x,y_pos,slide["symbol"])
        x += fm.horizontalAdvance(slide["symbol"]) + self.PADDING
        price_text = f"{slide['price']:.{self.decimals[self.current_index]}f}" if slide["price"] is not None else "..."
        painter.drawText(x,y_pos,price_text)

    # --- input & menu ---
    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            self._drag_pos=event.globalPosition().toPoint()-self.frameGeometry().topLeft()
    def mouseMoveEvent(self,event):
        if event.buttons()==Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint()-self._drag_pos)
    def mouseReleaseEvent(self,event):
        pos=self.pos()
        config["pos_x"],config["pos_y"]=pos.x(),pos.y()
        save_settings()
    def contextMenuEvent(self,event):
        menu=QMenu(self)
        settings_action=QAction("Settings",self)
        exit_action=QAction("Quit",self)
        menu.addAction(settings_action); menu.addAction(exit_action)
        action=menu.exec(event.globalPos())
        if action==settings_action: self.open_settings()
        elif action==exit_action: QApplication.instance().quit()
    def open_settings(self):
        dlg=SettingsDialog(self)
        dlg.exec()
    def apply_settings(self):
        self.symbols=[config["symbol1"],config["symbol2"],config["symbol3"]]
        self.decimals=[config["decimals1"],config["decimals2"],config["decimals3"]]
        # reload slides
        self.slides.clear()
        for s in self.symbols:
            self.slides[s] = {
                "icon": make_fallback_pixmap(s.replace("USDT",""),size=128),
                "symbol": s.replace("USDT",""),
                "price": None
            }
        self.current_index=0
        self.slide_offset=0
        self.slide_in_progress=False
        self.reload_icons_async()
        self.update_prices()
        self._resize_to_content()
        self.update()
        self.update_timer.stop(); self.update_timer.start(max(5,config.get("update_interval",30))*1000)
        self.cycle_timer.stop()
        if config.get("cycle_enabled",True):
            self.cycle_timer.start(max(3,config.get("cycle_interval",3))*1000)

# ---------- app entry ----------
def main():
    load_settings()
    app=QApplication(sys.argv)
    app.setApplicationName("Crypto Widget")
    app.setStyleSheet("QWidget { font-family: Arial; }")
    widget=CryptoWidget()
    widget.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
