from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from tkinter import filedialog
from tkinter import Tk

class TelaDesenho(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1)  # Define a cor para branco (R, G, B)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self.atualizar_fundo, pos=self.atualizar_fundo)
            self.modo = 'pincel'  # Modo inicial como pincel
            self.linha_cor = (0, 0, 0)  # Cor preta como padrão

            self.cor_fundo = (1, 1, 1, 1)  # Cor branca como padrão para o fundo
            self.borracha_tamanho = 20  # Tamanho da borracha

    def atualizar_fundo(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

        self.modo = 'pincel'  # Modo inicial como pincel
        self.linha_cor = (0, 0, 0)  # Cor preta como padrão

    def linha_colide(self, touch, line):
        # Verifica se o toque está próximo de algum ponto da linha
        for point in zip(line.points[::2], line.points[1::2]):
            if self.collide_ponto(touch.x, touch.y, point[0], point[1]):
                return True
        return False

    def collide_ponto(self, x, y, px, py, raio=10):
        # Verifica se o ponto (x, y) está dentro de um raio do ponto (px, py)
        return (px - raio <= x <= px + raio) and (py - raio <= y <= py + raio)

    def on_touch_down(self, touch):
        if self.modo == 'borracha':
            self.apagar_com_borracha(touch)
        else:
            with self.canvas:
                Color(*self.linha_cor)
                linha = Line(points=(touch.x, touch.y), width=2)
                touch.ud['linha'] = linha
                
    def on_touch_move(self, touch):
        if self.modo == 'borracha':
            self.apagar_com_borracha(touch)
        elif 'linha' in touch.ud:
            touch.ud['linha'].points += [touch.x, touch.y]

    def apagar_com_borracha(self, touch):
        # Desenha com a cor de fundo para simular a borracha
        with self.canvas:
            Color(*self.cor_fundo)
            d = self.borracha_tamanho
            Line(circle=(touch.x, touch.y, d / 2), width=d)

    def mudar_para_borracha(self):
        self.modo = 'borracha'

    def mudar_para_pincel(self):
        self.modo = 'pincel'
        self.linha_cor = (0, 0, 0)  # Volta para a cor preta
            
    def salvar_desenho(self, *args):
        Tk().withdraw()  # Esconde a janela principal do Tk
        caminho_salvar = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG files', '*.png')],
            title="Escolha onde salvar o desenho"
        )
        if caminho_salvar:
            self.export_to_png(caminho_salvar)  # Salva o desenho no caminho especificado
    
    def limpar_tela(self, *args):
        self.canvas.clear()

class FerramentasPopup(Popup):
    def __init__(self, tela_desenho, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)

        # Tamanho da janela de ferramentas 
        self.size = (600, 600)
        self.tela_desenho = tela_desenho

        # Se a tela de denho vai estar aberta ou não
        self.is_open = False

        # Conteúdo do Popup
        box = BoxLayout(orientation='vertical')

        # Seletor de cor
        self.color_picker = ColorPicker(size_hint=(1, 1.2), size=(400, 700))
        box.add_widget(self.color_picker)
        self.color_picker.bind(color=self.on_color)

        # Slider para espessura da linha
        self.slider = Slider(min=1, max=10, value=1)
        box.add_widget(self.slider)
        self.slider.bind(value=self.on_thickness)

        self.content = box

    def on_color(self, instance, value):
        self.tela_desenho.linha_cor = value

    def on_thickness(self, instance, value):
        self.tela_desenho.linha_espessura = value

class DesenhoApp(App):
    def build(self):
        root = BoxLayout(orientation='horizontal')

        tela_desenho = TelaDesenho()
        root.add_widget(tela_desenho)

        # Loyout dos botões
        botoes_layout = BoxLayout(orientation='vertical', size_hint=(None, 1), width=150)

        # Botão limpar tela
        clear_btn = Button(text='Limpar Tela', size_hint=(1, None), height=50)
        clear_btn.bind(on_release=tela_desenho.limpar_tela)
        botoes_layout.add_widget(clear_btn)

        # Botão salvar
        save_btn = Button(text='Salvar Desenho', size_hint=(1, None), height=50)
        save_btn.bind(on_release=tela_desenho.salvar_desenho)
        botoes_layout.add_widget(save_btn)

        # Botão ferramentas
        ferramentas_btn = Button(text='Ferramentas', size_hint=(1, None), height=50)
        ferramentas_btn.bind(on_release=self.abrir_ferramentas)
        botoes_layout.add_widget(ferramentas_btn)

        # Botão pincel
        pincel_btn = Button(text='Pincel', size_hint=(1, None), height=50)
        pincel_btn.bind(on_release=lambda x: tela_desenho.mudar_para_pincel())
        botoes_layout.add_widget(pincel_btn)

        # Botão borracha
        borracha_btn = Button(text='Borracha', size_hint=(1, None), height=50)
        borracha_btn.bind(on_release=lambda x: tela_desenho.mudar_para_borracha())
        botoes_layout.add_widget(borracha_btn)


        root.add_widget(botoes_layout)

        self.ferramentas_popup = FerramentasPopup(tela_desenho)

        return root

    def abrir_ferramentas(self, instance):
        # Verifica se o popup já está aberto
        if not self.ferramentas_popup.is_open:
            self.ferramentas_popup.open()
            self.ferramentas_popup.is_open = True 
        else:
            self.ferramentas_popup.dismiss()  # Fecha o popup se já estiver aberto
            self.ferramentas_popup.is_open = False 

if __name__ == '__main__':
    DesenhoApp().run()