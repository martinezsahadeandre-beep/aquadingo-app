"""
AquaDingo 💧 - versão Android (Kivy)
App estilo Duolingo para beber água e bater metas diárias.
"""
import random
from datetime import date, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.metrics import dp

from data_logic import (
    DEFAULT_DATA, CONQUISTAS, FRASES_MOTIVACIONAIS, FRASES_META_BATIDA,
    FRASES_LEMBRETE, carregar_dados, salvar_dados, processar_virada_de_dia,
    checar_novas_conquistas, adicionar_agua, nivel_de, xp_para_proximo_nivel,
    hoje_str,
)

try:
    from plyer import notification
    NOTIFICACOES_DISPONIVEIS = True
except Exception:
    NOTIFICACOES_DISPONIVEIS = False

COR_FUNDO = (0.92, 0.96, 1, 1)
COR_PRIMARIA = (0.11, 0.69, 0.96, 1)
COR_SUCESSO = (0.345, 0.8, 0.008, 1)
COR_XP = (1, 0.78, 0, 1)
COR_STREAK = (1, 0.588, 0, 1)
COR_TEXTO = (0.24, 0.24, 0.24, 1)
COR_BLOQUEADO = (0.75, 0.75, 0.75, 1)


class AnelProgresso(Widget):
    """Widget de círculo de progresso desenhado com kivy.graphics."""
    percentual = NumericProperty(0)  # 0 a 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._desenhar, size=self._desenhar, percentual=self._desenhar)

    def _desenhar(self, *args):
        self.canvas.clear()
        with self.canvas:
            tam = min(self.width, self.height)
            espessura = dp(14)
            x = self.center_x - tam / 2
            y = self.center_y - tam / 2

            Color(0.86, 0.93, 1, 1)
            Line(circle=(self.center_x, self.center_y, tam / 2 - espessura / 2), width=espessura)

            if self.percentual > 0:
                cor = COR_SUCESSO if self.percentual >= 1 else COR_PRIMARIA
                Color(*cor)
                angulo = 360 * min(1, self.percentual)
                Line(circle=(self.center_x, self.center_y, tam / 2 - espessura / 2,
                              90, 90 - angulo), width=espessura, cap="round")


KV = """
ScreenManager:
    MainScreen:
    AchievementsScreen:
    SettingsScreen:

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: 0.92, 0.96, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(110)
            canvas.before:
                Color:
                    rgba: 0.11, 0.69, 0.96, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "\\U0001F4A7 AquaDingo"
                font_size: dp(24)
                bold: True
                color: 1,1,1,1
                size_hint_y: None
                height: dp(40)
            BoxLayout:
                size_hint_y: None
                height: dp(30)
                Label:
                    id: lbl_streak
                    text: "0 dias"
                    color: 1,1,1,1
                Label:
                    id: lbl_nivel
                    text: "Nivel 1"
                    color: 1,1,1,1
                Label:
                    id: lbl_xp
                    text: "0 XP"
                    color: 1,1,1,1

        ScrollView:
            BoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16)
                spacing: dp(12)

                BoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: dp(320)
                    canvas.before:
                        Color:
                            rgba: 1,1,1,1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    padding: dp(12)
                    spacing: dp(6)

                    Label:
                        text: "Meta de hoje"
                        color: 0.24,0.24,0.24,1
                        bold: True
                        size_hint_y: None
                        height: dp(28)

                    FloatLayout:
                        size_hint_y: None
                        height: dp(200)
                        AnelProgresso:
                            id: anel
                            size_hint: None, None
                            size: dp(180), dp(180)
                            pos_hint: {"center_x": 0.5, "center_y": 0.5}
                        Label:
                            id: lbl_pct
                            text: "0%"
                            font_size: dp(30)
                            bold: True
                            color: 0.11,0.69,0.96,1
                            pos_hint: {"center_x": 0.5, "center_y": 0.55}
                        Label:
                            text: "da meta"
                            color: 0.24,0.24,0.24,1
                            pos_hint: {"center_x": 0.5, "center_y": 0.42}

                    Label:
                        id: lbl_ml
                        text: "0 ml / 2000 ml"
                        bold: True
                        color: 0.24,0.24,0.24,1
                        size_hint_y: None
                        height: dp(24)

                BoxLayout:
                    size_hint_y: None
                    height: dp(70)
                    spacing: dp(8)
                    Button:
                        text: "Copo\\n250ml"
                        background_color: 0.345, 0.8, 0.008, 1
                        on_release: app.adicionar_agua(250)
                    Button:
                        text: "Garrafa\\n500ml"
                        background_color: 0.345, 0.8, 0.008, 1
                        on_release: app.adicionar_agua(500)
                    Button:
                        text: "Litro\\n1000ml"
                        background_color: 0.345, 0.8, 0.008, 1
                        on_release: app.adicionar_agua(1000)

                BoxLayout:
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(8)
                    TextInput:
                        id: entrada_custom
                        hint_text: "ml"
                        multiline: False
                        input_filter: "int"
                    Button:
                        text: "Adicionar"
                        size_hint_x: 0.6
                        background_color: 0.11, 0.69, 0.96, 1
                        on_release: app.adicionar_custom(entrada_custom)
                    Button:
                        text: "Desfazer"
                        size_hint_x: 0.6
                        background_color: 0.9, 0.9, 0.9, 1
                        color: 0.2,0.2,0.2,1
                        on_release: app.desfazer()

                BoxLayout:
                    size_hint_y: None
                    height: dp(70)
                    canvas.before:
                        Color:
                            rgba: 1, 0.965, 0.86, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    padding: dp(10)
                    Label:
                        id: lbl_mascote
                        text: "Gotinha diz: oi!"
                        color: 0.48, 0.36, 0, 1
                        text_size: self.width, None
                        halign: "left"
                        valign: "middle"

                BoxLayout:
                    size_hint_y: None
                    height: dp(50)
                    spacing: dp(8)
                    Button:
                        text: "Conquistas"
                        background_color: 0.94,0.94,0.94,1
                        color: 0.2,0.2,0.2,1
                        on_release: app.abrir_conquistas()
                    Button:
                        text: "Ajustes"
                        background_color: 0.94,0.94,0.94,1
                        color: 0.2,0.2,0.2,1
                        on_release: app.abrir_ajustes()


<AchievementsScreen>:
    name: "conquistas"
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: 0.92, 0.96, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: dp(8)
            Button:
                text: "< Voltar"
                size_hint_x: 0.3
                on_release: app.ir_para("main")
            Label:
                text: "Conquistas"
                bold: True
                color: 0.24,0.24,0.24,1
        ScrollView:
            BoxLayout:
                id: lista_conquistas
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(12)
                spacing: dp(8)


<SettingsScreen>:
    name: "ajustes"
    BoxLayout:
        orientation: "vertical"
        canvas.before:
            Color:
                rgba: 0.92, 0.96, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: dp(8)
            Button:
                text: "< Voltar"
                size_hint_x: 0.3
                on_release: app.ir_para("main")
            Label:
                text: "Ajustes"
                bold: True
                color: 0.24,0.24,0.24,1

        BoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(10)
            size_hint_y: None
            height: dp(260)

            Label:
                text: "Meta diaria (ml)"
                color: 0.24,0.24,0.24,1
                size_hint_y: None
                height: dp(24)
            TextInput:
                id: entrada_meta
                multiline: False
                input_filter: "int"
                size_hint_y: None
                height: dp(44)

            Label:
                text: "Intervalo de lembrete (min)"
                color: 0.24,0.24,0.24,1
                size_hint_y: None
                height: dp(24)
            TextInput:
                id: entrada_intervalo
                multiline: False
                input_filter: "int"
                size_hint_y: None
                height: dp(44)

            Button:
                text: "Salvar"
                background_color: 0.11, 0.69, 0.96, 1
                size_hint_y: None
                height: dp(48)
                on_release: app.salvar_ajustes(entrada_meta.text, entrada_intervalo.text)

            Button:
                text: "Zerar todos os dados"
                background_color: 1, 0.87, 0.87, 1
                color: 0.64, 0, 0, 1
                size_hint_y: None
                height: dp(48)
                on_release: app.zerar_dados()
"""


class MainScreen(Screen):
    pass


class AchievementsScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class AquaDingoApp(App):
    def build(self):
        self.dados = carregar_dados()
        self.dados = processar_virada_de_dia(self.dados)
        salvar_dados(self.dados)
        self.frase_atual = random.choice(FRASES_MOTIVACIONAIS)
        self._ultimo_ml_adicionado = 0

        self.sm = Builder.load_string(KV)
        return self.sm

    def on_start(self):
        self.atualizar_tela_principal()
        Clock.schedule_interval(self._checar_virada_dia, 5 * 60)
        self._agendar_lembrete()

    # ---------------- ações principais ----------------

    def adicionar_agua(self, ml):
        bateu_meta = adicionar_agua(self.dados, ml)
        self._ultimo_ml_adicionado = ml
        if bateu_meta:
            self.frase_atual = random.choice(FRASES_META_BATIDA)
            self._popup_info("Meta batida! 🎉",
                              "Parabens! Voce bateu sua meta de agua hoje!\n+50 XP de bonus!")
        else:
            self.frase_atual = random.choice(FRASES_MOTIVACIONAIS)

        salvar_dados(self.dados)
        novas = checar_novas_conquistas(self.dados)
        if novas:
            salvar_dados(self.dados)
            texto = "\n".join(f"- {c['nome']}: {c['desc']}" for c in novas)
            self._popup_info("Nova(s) conquista(s)!", texto)

        self.atualizar_tela_principal()

    def adicionar_custom(self, campo_texto):
        valor = campo_texto.text.strip()
        if not valor:
            return
        try:
            ml = int(valor)
        except ValueError:
            self._popup_info("Valor invalido", "Digite um numero de ml valido.")
            return
        self.adicionar_agua(ml)
        campo_texto.text = ""

    def desfazer(self):
        ml = self._ultimo_ml_adicionado
        if ml <= 0:
            return
        self.dados["hoje_ml"] = max(0, self.dados["hoje_ml"] - ml)
        self.dados["xp"] = max(0, self.dados["xp"] - max(1, ml // 10))
        self._ultimo_ml_adicionado = 0
        salvar_dados(self.dados)
        self.atualizar_tela_principal()

    # ---------------- navegação ----------------

    def ir_para(self, nome_tela):
        if nome_tela == "conquistas":
            self._popular_conquistas()
        self.sm.current = nome_tela

    def abrir_conquistas(self):
        self.ir_para("conquistas")

    def abrir_ajustes(self):
        tela = self.sm.get_screen("ajustes")
        tela.ids.entrada_meta.text = str(self.dados["meta_ml"])
        tela.ids.entrada_intervalo.text = str(self.dados["intervalo_lembrete_min"])
        self.ir_para("ajustes")

    def salvar_ajustes(self, meta_texto, intervalo_texto):
        try:
            meta = int(meta_texto)
            intervalo = int(intervalo_texto)
            if meta <= 0 or intervalo <= 0:
                raise ValueError
        except ValueError:
            self._popup_info("Valor invalido", "Use apenas numeros positivos.")
            return
        self.dados["meta_ml"] = meta
        self.dados["intervalo_lembrete_min"] = intervalo
        salvar_dados(self.dados)
        self.atualizar_tela_principal()
        self.ir_para("main")

    def zerar_dados(self):
        self.dados = dict(DEFAULT_DATA)
        self.dados["historico"] = {}
        self.dados["conquistas"] = []
        self.dados["ultimo_dia_ativo"] = hoje_str()
        salvar_dados(self.dados)
        self.atualizar_tela_principal()
        self.ir_para("main")

    # ---------------- atualização visual ----------------

    def atualizar_tela_principal(self):
        tela = self.sm.get_screen("main")
        d = self.dados
        nivel = nivel_de(d["xp"])

        tela.ids.lbl_streak.text = f"{d['streak']} dias"
        tela.ids.lbl_nivel.text = f"Nivel {nivel}"
        tela.ids.lbl_xp.text = f"{d['xp']} XP"

        meta = d["meta_ml"]
        bebido = d["hoje_ml"]
        pct = min(1.0, bebido / meta) if meta else 0
        tela.ids.anel.percentual = pct
        tela.ids.lbl_pct.text = f"{int(pct*100)}%"
        tela.ids.lbl_ml.text = f"{bebido} ml / {meta} ml"
        tela.ids.lbl_mascote.text = f"Gotinha diz: \"{self.frase_atual}\""

    def _popular_conquistas(self):
        tela = self.sm.get_screen("conquistas")
        container = tela.ids.lista_conquistas
        container.clear_widgets()
        for c in CONQUISTAS:
            desbloqueada = c["id"] in self.dados["conquistas"]
            item = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(60))
            titulo = "[OK] " if desbloqueada else "[BLOQ] "
            lbl = Label(text=f"{titulo}{c['nome']}\n{c['desc']}",
                        color=COR_SUCESSO if desbloqueada else COR_BLOQUEADO,
                        halign="left")
            item.add_widget(lbl)
            container.add_widget(item)

    # ---------------- lembretes e virada de dia ----------------

    def _agendar_lembrete(self):
        intervalo_seg = max(1, self.dados.get("intervalo_lembrete_min", 60)) * 60
        Clock.schedule_interval(self._disparar_lembrete, intervalo_seg)

    def _disparar_lembrete(self, dt):
        if not self.dados.get("lembretes_ativos", True):
            return
        texto = random.choice(FRASES_LEMBRETE)
        if NOTIFICACOES_DISPONIVEIS:
            try:
                notification.notify(title="AquaDingo 💧", message=texto, timeout=5)
            except Exception:
                self._popup_info("AquaDingo", texto)
        else:
            self._popup_info("AquaDingo", texto)

    def _checar_virada_dia(self, dt):
        antigo = self.dados.get("ultimo_dia_ativo")
        self.dados = processar_virada_de_dia(self.dados)
        if antigo != self.dados["ultimo_dia_ativo"]:
            salvar_dados(self.dados)
            self.atualizar_tela_principal()

    def on_stop(self):
        salvar_dados(self.dados)

    # ---------------- utilitário ----------------

    def _popup_info(self, titulo, texto):
        conteudo = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        conteudo.add_widget(Label(text=texto))
        popup = Popup(title=titulo, content=conteudo,
                       size_hint=(0.85, 0.4))
        btn_fechar = Button(text="OK", size_hint_y=None, height=dp(44))
        conteudo.add_widget(btn_fechar)
        btn_fechar.bind(on_release=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    AquaDingoApp().run()
