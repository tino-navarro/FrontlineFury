import os
import pygame
from pygame import mixer
import random
import csv
from recursos import button
from datetime import datetime
import json
import tkinter as tk
import math

import pyttsx3
import speech_recognition as sr


tts_engine = pyttsx3.init()
recognizer = sr.Recognizer()

mixer.init()
pygame.init()

icone = pygame.image.load('recursos/frontlinefury.png')
pygame.display.set_icon(icone)

largura_tela = 1000
altura_tela = 700
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption('Frontline Fury')


# DEFINIÇÕES PARA AÇÕES DO JOGADOR
andar_esquerda = False
andar_direita = False
atirando = False
granada = False
granada_atirar = False

# DEFINE VARIÁVEIS DO JOGO
gravidade = 0.5
SCROLL_THRESH = 300
TAMANHO_BLOCO = 40
linhas = 16
colunas = 150
TAMANHO_BLOCO = altura_tela // linhas
tipos_textura = 15
tela_scroll = 0
bg_scroll = 0
level = 1
MAX_LEVELS = 3
iniciar_jogo = False
iniciar_intro = False

jogo_pausado = False
pontos = 0
log_salvo_nesta_vida = False


menu_estado = 'pedir_nome'
nome_jogador = ''


som_pulo = pygame.mixer.Sound('recursos/audios/audio_jump.wav')
som_pulo.set_volume(0.2)

som_tiro = pygame.mixer.Sound('recursos/audios/audio_shot.wav')
som_tiro.set_volume(0.5)

som_granada = pygame.mixer.Sound('recursos/audios/audio_grenade.wav')
som_granada.set_volume(0.9)

# IMAGEM PULSANTE
cobra_fuma = pygame.image.load('recursos/img/pixelated_image_detailed.png')
cobra_fuma = pygame.transform.scale(cobra_fuma, (100, 100))

# Folhas background 
folha_img = pygame.image.load('recursos/img/ambiente/folha.png').convert_alpha()
folha_img = pygame.transform.scale(folha_img, (20, 20))



# imagem dos botões do menu PAUSE
pause_background = pygame.image.load(
    'recursos/img/menu pause/PAUSE PRESET.png').convert_alpha()
pause_background = pygame.transform.scale(pause_background, (250, 250))
voltar_img = pygame.image.load(
    'recursos/img/menu pause/BTN BACK.png',).convert_alpha()
voltar_img = pygame.transform.scale(voltar_img, (100, 50))
sair_img = pygame.image.load(
    'recursos/img/Main menu/BTN Exit.png').convert_alpha()


# imagem dos botões do menu
play_img = pygame.image.load(
    'recursos/img/Main menu/BTN PLAY.png').convert_alpha()
exit_img = pygame.image.load(
    'recursos/img/Main menu/BTN Exit.png').convert_alpha()
restart_img = pygame.image.load(
    'recursos/img/restart/BTN Retry.png').convert_alpha()

# Carregar O BACKGROUND
tela_fundo = pygame.image.load(
    'recursos/img/background/2304x1296.png').convert_alpha()


# GUARDA TEXTURAS NA LISTA
img_list = []
for x in range(tipos_textura):
    img = pygame.image.load(f'recursos/img/texturas/{x}.png')
    img = pygame.transform.scale(img, (TAMANHO_BLOCO, TAMANHO_BLOCO))
    img_list.append(img)
# FLECHA
imagem_flecha = pygame.image.load(
    'recursos/img/jogador/Flecha/0.png').convert_alpha()
imagem_granada = pygame.image.load(
    'recursos/img/granada/granada.png').convert_alpha()
imagem_caixa_cura = pygame.image.load(
    'recursos/img/caixa_vida/caixa_vida.png').convert_alpha()
imagem_caixa_municao = pygame.image.load(
    'recursos/img/caixa_municao/caixa_municao.png').convert_alpha()
imagem_caixa_granada = pygame.image.load(
    'recursos/img/caixa_granada/caixa_granada.png').convert_alpha()

item_caixas = {
    'Saude': imagem_caixa_cura,
    'Munição': imagem_caixa_municao,
    'Granada': imagem_caixa_granada
}

# DEFINE O FPS 'frame por segundo'
fps = pygame.time.Clock()

# DEFINIR CORES
BG = (200, 200, 200)
vermelho = (255, 0, 0)
branco = (255, 255, 255)
verde = (0, 255, 0)
preto = (0, 0, 0)
ROSA = (235, 65, 54)

# DEFINE A FONTE:
font = pygame.font.SysFont('Futura', 30)


def inicializarBancoDeDados():
    # r - read, w - write, a - append
    try:
        banco = open("base.atitus", "r")
    except:
        print("Banco de Dados Inexistente. Criando...")
        banco = open("base.atitus", "w")

# FUNCAO PARA SALVAR O LOG


def salvar_log(nome, pontos):
    """
    Lê a base de dados JSON, adiciona um novo registro (ou sobrescreve se for 'Recruta')
    e salva a base de dados atualizada.
    """
    # Garante que não vamos salvar um log para um nome vazio
    if not nome:
        print("Nome do jogador vazio, log não salvo.")
        return

    # 1. Leitura segura do arquivo
    try:
        with open("log.dat", "r", encoding='utf-8') as banco:
            # json.load lê diretamente do arquivo. Se estiver vazio, trata o erro.
            # O .read(1) é um truque para checar se o arquivo está vazio sem carregar tudo.
            dadosDict = json.load(banco) if banco.read(1) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existe ou está corrompido, começamos com um dicionário vazio.
        dadosDict = {}

    # 2. Prepara os dados da nova partida
    agora = datetime.now()
    data_br = agora.strftime("%d/%m/%Y")
    hora_br = agora.strftime("%H:%M:%S")
    nova_partida = {"pontos": pontos, "data": data_br, "hora": hora_br}

    # 3. LÓGICA DE SALVAMENTO CORRIGIDA
    if nome == "Recruta":
        # REGRA 1: Para 'Recruta', sempre CRIE ou SOBRESCREVA a entrada.
        # Não usamos .append() aqui. Simplesmente definimos o valor.
        dadosDict[nome] = [nova_partida]
    else:
        # REGRA 2: Para jogadores nomeados, mantenha o histórico.
        if nome in dadosDict:
            # Se o jogador já existe, adicione à sua lista.
            dadosDict[nome].append(nova_partida)
        else:
            # Se é um jogador novo, crie a chave e a lista com a primeira partida.
            dadosDict[nome] = [nova_partida]

    # 4. Escrita segura no arquivo
    try:
        with open("log.dat", "w", encoding='utf-8') as banco:
            json.dump(dadosDict, banco, indent=4, ensure_ascii=False)
        print(f"Log salvo para o jogador {nome}: {nova_partida}")
    except Exception as e:
        print(f"Ocorreu um erro ao tentar salvar os dados: {e}")


def obter_ranking():
    try:
        with open("log.dat", "r", encoding='utf-8') as banco:
            dados = json.load(banco)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existe ou está corrompido, retorna uma lista vazia.
        return []

    todas_as_partidas = []
    # Itera através de cada jogador (chave) e sua lista de partidas (valor)
    for nome, partidas in dados.items():
        # Para cada partida na lista de um jogador
        for partida in partidas:
            # Adiciona uma tupla (pontos, nome) à nossa lista geral
            todas_as_partidas.append((partida['pontos'], nome))

    # Ordena a lista de todas as partidas.
    # key=lambda item: item[0] diz para ordenar pelo primeiro elemento da tupla (os pontos).
    # reverse=True faz a ordenação do maior para o menor.
    partidas_ordenadas = sorted(
        todas_as_partidas, key=lambda item: item[0], reverse=True)

    # Retorna apenas os 5 primeiros resultados
    return partidas_ordenadas[:5]


def desenhar_ranking(ranking, x, y):
    """
    Desenha o ranking formatado na tela.
    """
    # Título do Ranking
    desenhar_texto("MELHORES PONTUAÇÕES", font, ROSA, x, y)

    # Itera através da lista de ranking e desenha cada entrada
    # O enumerate(..., start=1) nos dá a posição (1º, 2º, 3º...) automaticamente
    altura_linha = 40
    for posicao, (pontos, nome) in enumerate(ranking, start=1):
        texto_ranking = f"{posicao}º - {nome.upper()} - {pontos} PONTOS"
        desenhar_texto(texto_ranking, font, branco, x,
                       y + (posicao * altura_linha))


def falar(texto):
    print(f'CORONEL:{texto}')
    tts_engine.say(texto)
    tts_engine.runAndWait()


def ouvir():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Diga seu nome de guerra! ")

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            print('Ouvindo...')
            nome = recognizer.recognize_google(audio, language='pt-BR')
            return nome.capitalize()

        except sr.UnknownValueError:
            print('Não consegui entender o que você disse.')
            return None
        except sr.RequestError as e:
            print(f"Erro na requisição ao serviço do Google; {e}")
            return None
        except sr.WaitTimeoutError:
            print("Tempo de escuta esgotado. Ninguém falou nada.")
            return None


def desenhar_texto(text, font, texto_coluna, x, y):
    imagem_texto = font.render(text, True, texto_coluna)
    tela.blit(imagem_texto, (x, y))


def tela_background():
    tela.fill(BG)
    width = tela_fundo.get_width()
    for x in range(5):
        tela.blit(tela_fundo, ((x * width - bg_scroll, 0)))


# FUNÇÃO PARA REINICIAR O NIVEL


def reiniciar_nivel():
    grupo_esqueleto.empty()
    grupo_flecha.empty()
    grupo_granada.empty()
    grupo_explosão.empty()
    grupo_caixas_itens.empty()
    grupo_decoracao.empty()
    grupo_agua.empty()
    grupo_saida.empty()

    # CRIA LISTAS DE BLOCOS VAZIAS
    data = []
    for linha in range(linhas):
        r = [-1] * colunas
        data.append(r)

    return data


# CONFIGURA O PERSONAGEM PARA APARECER NA TELA E TAMBÉM SEU TAMANHO
class Cavaleiro(pygame.sprite.Sprite):
    def __init__(self, tipo_personagem, x, y, escala, velocidade, munição, granadas):
        pygame.sprite.Sprite.__init__(self)
        self.vida = True
        self.atacando = False
        self.tipo_personagem = tipo_personagem
        self.velocidade = velocidade
        self.munição = munição
        self.munição_inicial = munição
        self.flecha_cooldown = 0
        self.granadas = granadas
        self.saúde = 100
        self.saúde_maxima = self.saúde
        self.direção = 1
        self.velocidade_queda = 0
        self.pulo = False
        self.no_ar = True
        self.flip = False
        self.lista_animação = []
        self.index = 0
        self.action = 0
        self.atualiza_tempo = pygame.time.get_ticks()
        # VARIÁVEIS DA IA
        self.movimentação_contagem = 0
        self.visao = pygame.Rect(0, 0, 150, 20)
        self.parado = False
        self.contagem_parado = 0

        tipos_animações = ['Idle', 'Andar', 'Pular', 'Flecha', 'Morte']
        lista_temp = []
        for animação in tipos_animações:
            # REINICIA LISTA TEMPORARIA DE IMAGENS
            lista_temp = []
            # CONTE OS NUMEROS DE IMAGENS NA PASTA
            num_de_imagem = len(os.listdir(
                f'recursos/img/{self.tipo_personagem}/{animação}'))
            for i in range(num_de_imagem):
                personagem = pygame.image.load(
                    f'recursos/img/{self.tipo_personagem}/{animação}/{i}.png').convert_alpha()
                personagem = pygame.transform.scale(
                    personagem, (personagem.get_width() * escala, personagem.get_height() * escala))
                lista_temp.append(personagem)
            self.lista_animação.append(lista_temp)

        self.image = self.lista_animação[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.atualizar_animação()
        self.verifica_vida()
        # atualiza cooldown
        if self.flecha_cooldown > 0:
            self.flecha_cooldown -= 1

    def movimentação(self, andar_esquerda, andar_direita):
        # MANIPULAÇÃO DE DIREÇÃO E VELOCIDADE DO PERSONAGEM
        tela_scroll = 0
        personagemX = 0
        personagemY = 0
        # ATRIBUIR VARIÁVEIS QUE CRIAM A MOVIMENTAÇÃO DO PERSONAGEM
        if andar_esquerda:
            personagemX = -self.velocidade
            self.flip = True
            self.direção = -1

        if andar_direita:
            personagemX = self.velocidade
            self.flip = False
            self.direção = 1

        # PULO
        if self.pulo == True and self.no_ar == False:
            self.velocidade_queda = -11
            self.pulo = False
            self.no_ar = True
        personagemY += self.velocidade_queda

        # APLICAR GRAVIDADE
        self.velocidade_queda += gravidade
        if self.velocidade_queda > 10:
            self.velocidade_queda
        personagemY += self.velocidade_queda

        # CHECA A COLISÃO COM O CHÃO

        for tile in world.lista_obstaculo:
            # checa a colisao na direção X
            if tile[1].colliderect(self.rect.x + personagemX, self.rect.y, self.width, self.height):
                personagemX = 0
                # SE A IA ATINGIR A PAREDE, FAZ COM QUE VIREM PARA O LADO CONTRARIO
                if self.tipo_personagem == 'esqueleto':
                    self.direção *= -1
                    self.movimentação_contagem = 0

                # checa pela colisao na direção Y
            if tile[1].colliderect(self.rect.x, self.rect.y + personagemY, self.width, self.height):
                # checa se estou abaixo do chão
                if self.velocidade_queda < 0:
                    self.velocidade_queda = 0
                    personagemY = tile[1].bottom - self.rect.top
                    # checa se estou acima do chao
                elif self.velocidade_queda >= 0:
                    self.velocidade_queda = 0
                    self.no_ar = False
                    personagemY = tile[1].top - self.rect.bottom

        # CHECA A COLISAO COM A AGUA
        if pygame.sprite.spritecollide(self, grupo_agua, False):
            self.saúde = 0

        # checa a colisao com a saída
        level_complete = False
        if pygame.sprite.spritecollide(self, grupo_saida, False):
            level_complete = True

        # CHECA SE CAIU DO MAPA
        if self.rect.bottom > altura_tela:
            self.health = 0

        # CHECA SE CHEGOU AO FINAL DO INICIO DA TELA
        if self.tipo_personagem == 'jogador':
            if self.rect.left + personagemX < 0 or self.rect.right + personagemX > largura_tela:
                personagemX = 0

        # ATUALIZAR A POSIÇÃO DO RETÂNGULO
        self.rect.x += personagemX
        self.rect.y += personagemY

        # ATUALIZA O SCROLL BASEADO NA POSIÇÃO DO JOGADOR
        if self.tipo_personagem == 'jogador':

            if (self.rect.right > largura_tela - SCROLL_THRESH and bg_scroll < (world.level_length * TAMANHO_BLOCO) - largura_tela)\
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(personagemX)):
                self.rect.x -= personagemX
                tela_scroll = -personagemX

        return tela_scroll, level_complete

    def Atacar(self):
        if self.flecha_cooldown == 0 and self.munição > 0:
            self.flecha_cooldown = 15
            nova_flecha = Flecha(self.rect.centerx + (
                # MANTEM ATACANDO
                0.6 * self.rect.size[0] * self.direção), self.rect.centery, self.direção)
            grupo_flecha.add(nova_flecha)
            self.munição -= 1
            som_tiro.play()

        if not self.atacando:
            self.atacando = True
            self.atualizar_ações(3)

    def ia(self):
        if self.vida and jogador.vida:
            if self.parado == False and random.randint(1, 200) == 1:
                self.atualizar_ações(0)  # ação parado
                self.parado = True
                self.contagem_parado = 50
            # CHECA SE A IA ESTÁ PERTO DO JOGADOR
            if self.visao.colliderect(jogador.rect):
                # para de correr ao encontrar o jogador
                self.atualizar_ações(0)  # parar
                # ATIRAR
                self.Atacar()
            else:
                if self.parado == False:
                    if self.direção == 1:
                        ia_andar_direita = True
                    else:
                        ia_andar_direita = False
                    ia_andar_esquerda = not ia_andar_direita
                    self.movimentação(ia_andar_esquerda, ia_andar_direita)
                    self.atualizar_ações(1)  # ação correr
                    self.movimentação_contagem += 1
                    # ATUALIZA A VISAO DA IA COM O MOVIMENTO DO INIMIGO
                    self.visao.center = (self.rect.centerx +
                                         75 * self.direção, self.rect.centery)

                    if self.movimentação_contagem > TAMANHO_BLOCO:
                        self.direção *= -1
                        self.movimentação_contagem *= -1
                else:
                    self.contagem_parado -= 1
                    if self.contagem_parado <= 0:
                        self.parado = False

            # scrollar
        self.rect.x += tela_scroll

    def atualizar_animação(self):
        # ATUALIZA ANIMAÇÃO
        atualização_animação = 200
        # ATUALIZA IMAGEM DEPENDENDO DO FRAME ATUAL
        self.image = self.lista_animação[self.action][self.index]
        # VERIFICA SE PASSOU TEMPO SUFICIENTE DESDE A ULTIMA ATUALIZAÇÃO
        if pygame.time.get_ticks() - self.atualiza_tempo > atualização_animação:
            self.atualiza_tempo = pygame.time.get_ticks()
            self.index += 1
        # SE A ANIMAÇÃO TERMINAR ELA VOLTA AO INICIO
        if self.index >= len(self.lista_animação[self.action]):
            if self.action == 4:
                self.index = len(self.lista_animação[self.action]) - 1
                self.kill()
            else:
                self.index = 0

        # SE TERMINOU O ATAQUE, VOLTAR AO IDLE
            if self.action == 3:
                self.atacando = False
                self.atualizar_ações(0)

    def atualizar_ações(self, nova_ação):
        # CHECA SE A NOVA AÇÃO É DIFERENTE DA ANTERIOR
        if nova_ação != self.action:
            self.action = nova_ação
            # ATUALIZA A ANIMAÇÃO
            self.index = 0
            self.atualiza_tempo = pygame.time.get_ticks()

    def verifica_vida(self):
        global pontos
        global menu_estado
        if self.saúde <= 0:
            self.saúde = 0
            self.velocidade = 0
            self.vida = False
            self.atualizar_ações(4)
            if self.tipo_personagem == 'jogador':
                menu_estado = 'morto'
            if self.tipo_personagem == 'esqueleto':
                pontos += 10

    def desenhar(self):
        tela.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.lista_obstaculo = []

    def processar_dados(self, dados):
        self.level_length = len(dados[0])
        jogador = None
        barra_vida = None
        # Lê cada valor no arquivo do level, csv
        for y, linha in enumerate(dados):
            for x, grade in enumerate(linha):
                if grade >= 0:
                    img = img_list[grade]
                    img_rect = img.get_rect()
                    img_rect.x = x * TAMANHO_BLOCO
                    img_rect.y = y * TAMANHO_BLOCO
                    tile_data = (img, img_rect)
                    if grade >= 0 and grade <= 4:
                        self.lista_obstaculo.append(tile_data)
                    elif grade >= 5 and grade <= 6:
                        agua = Agua(img,  x * TAMANHO_BLOCO, y * TAMANHO_BLOCO)
                        grupo_agua.add(agua)
                    elif grade >= 7 and grade <= 8:
                        decoracao = Decoração(
                            img,  x * TAMANHO_BLOCO, y * TAMANHO_BLOCO)
                        grupo_decoracao.add(decoracao)

                    elif grade == 9:  # CRIA O JOGADOR
                        jogador = Cavaleiro(
                            'jogador', x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, 2, 5, 25, 5)
                        barra_vida = BarraVida(
                            10, 10, jogador.saúde, jogador.saúde)
                    elif grade == 10:  # CRIA OS INIMIGOS
                        esqueleto = Cavaleiro(
                            'esqueleto', x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, 2, 2, 100, 0)
                        grupo_esqueleto.add(esqueleto)
                    elif grade == 11:  # CRIA CAIXA MUNIÇÕES
                        item_caixa = CaixaItens(
                            'Munição',  x * TAMANHO_BLOCO, y * TAMANHO_BLOCO)
                        grupo_caixas_itens.add(item_caixa)
                    elif grade == 12:  # CRIA CAIXA GRANADA
                        item_caixa = CaixaItens(
                            'Granada',  x * TAMANHO_BLOCO, y * TAMANHO_BLOCO)
                        grupo_caixas_itens.add(item_caixa)
                    elif grade == 13:  # CRIA CAIXA MUNIÇÕES
                        item_caixa = CaixaItens(
                            'Saude',  x * TAMANHO_BLOCO, y * TAMANHO_BLOCO)
                        grupo_caixas_itens.add(item_caixa)
                    elif grade == 14:  # cria saída
                        saida = Saida(img,  x * TAMANHO_BLOCO,
                                      y * TAMANHO_BLOCO)
                        grupo_saida.add(saida)
        return jogador, barra_vida

    def draw(self):
        for tile in self.lista_obstaculo:
            tile[1][0] += tela_scroll
            tela.blit(tile[0], tile[1])


class Decoração(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TAMANHO_BLOCO // 2, y +
                            (TAMANHO_BLOCO - self.image.get_height()))

    def update(self):
        self.rect.x += tela_scroll


class Agua(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TAMANHO_BLOCO // 2, y +
                            (TAMANHO_BLOCO - self.image.get_height()))

    def update(self):
        self.rect.x += tela_scroll


class Saida(pygame.sprite.Sprite):
    def __init__(self, img, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TAMANHO_BLOCO // 2, y +
                            (TAMANHO_BLOCO - self.image.get_height()))

    def update(self):
        self.rect.x += tela_scroll


class CaixaItens(pygame.sprite.Sprite):
    def __init__(self, tipo_item, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.tipo_item = tipo_item
        self.image = item_caixas[self.tipo_item]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TAMANHO_BLOCO // 2, y +
                            (TAMANHO_BLOCO - self.image.get_height()))

    def update(self):
        # SCROLLA
        self.rect.x += tela_scroll
        # CHECA SE O JOGADOR PEGOU A CAIXA
        if pygame.sprite.collide_rect(self, jogador):
            # CHECA QUAL TIPO DE CAIXA É
            if self.tipo_item == 'Saude':
                jogador.saúde += 25
                if jogador.saúde >= jogador.saúde_maxima:
                    jogador.saúde = jogador.saúde_maxima
            elif self.tipo_item == 'Munição':
                jogador.munição += 15
            elif self.tipo_item == 'Granada':
                jogador.granadas += 3
            # DELETA A CAIXA DE ITEM
            self.kill()


class BarraVida():
    def __init__(self, x, y, saúde, saúde_maxima):
        self.x = x
        self.y = y
        self.saúde = saúde
        self.saúde_maxima = saúde_maxima

    def desenhar(self, saúde):
        self.saúde = saúde
        # calcula a quantia de vida
        ratio = self.saúde / self.saúde_maxima
        pygame.draw.rect(tela, preto, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(tela, vermelho, (self.x, self.y, 150, 20))
        pygame.draw.rect(tela, verde, (self.x, self.y, 150 * ratio, 20))


class Flecha(pygame.sprite.Sprite):
    def __init__(self, x, y, direção):
        pygame.sprite.Sprite.__init__(self)
        self.velocidade = 10
        self.image = imagem_flecha
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direção = direção

    def update(self):
        # mover flecha
        self.rect.x += (self.direção * self.velocidade) + tela_scroll
        # checa se a flecha ja saiu da tela
        if self.rect.right < 0 or self.rect.left > 1000:
            self.kill()

        # checa a colisao com o nivel
        for tile in world.lista_obstaculo:
            if tile[1].colliderect(self.rect):
                self.kill()

        # CHECA COLISÃO ENTRE PERSONAGENS
        if pygame.sprite.spritecollide(jogador, grupo_flecha, False):
            if jogador.vida:
                jogador.saúde -= 5
                self.kill()
        for esqueleto in grupo_esqueleto:
            if pygame.sprite.spritecollide(esqueleto, grupo_flecha, False):
                if esqueleto.vida:
                    esqueleto.saúde -= 25
                    self.kill()


class Granada(pygame.sprite.Sprite):
    def __init__(self, x, y, direção):
        pygame.sprite.Sprite.__init__(self)
        self.temporizador = 100
        self.velocidade_queda = -11
        self.velocidade = 7
        self.image = imagem_granada
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direção = direção

    def update(self):
        self.velocidade_queda += gravidade
        granada_x = self.direção * self.velocidade
        granada_y = self.velocidade_queda

        # checa a colisao com o nivel
        for tile in world.lista_obstaculo:
            if tile[1].colliderect(self.rect.x + granada_y, self.rect.y, self.width, self.height):
                self.direção *= -1
                granada_x = self.direção * self.velocidade
            if tile[1].colliderect(self.rect.x, self.rect.y + granada_y, self.width, self.height):
                self.velocidade = 0
                # checa se estou abaixo do chão
                if self.velocidade_queda < 0:
                    self.velocidade_queda = 0
                    granada_y = tile[1].bottom - self.rect.top
                    # checa se estou acima do chao
                elif self.velocidade_queda >= 0:
                    self.velocidade_queda = 0
                    granada_y = tile[1].top - self.rect.bottom

        # ATUALIZA POSIÇÃO DA GRANADA
        self.rect.x += granada_x + tela_scroll
        self.rect.y += granada_y

        # CRONOMETRO PARA EXPLODIR
        self.temporizador -= 1
        if self.temporizador <= 0:
            self.kill()
            som_granada.play()
            explosão = Explosão(self.rect.x, self.rect.y, 0.5)
            grupo_explosão.add(explosão)
            # DAR DANO A QUALQUER QUE ESTEJA PERTO
            if abs(self.rect.centerx - jogador.rect.centerx) < TAMANHO_BLOCO * 2 and \
                    abs(self.rect.centery - jogador.rect.centery) < TAMANHO_BLOCO * 2:
                jogador.saúde -= 50
            for esqueleto in grupo_esqueleto:
                if abs(self.rect.centerx - esqueleto.rect.centerx) < TAMANHO_BLOCO * 2 and \
                        abs(self.rect.centery - esqueleto.rect.centery) < TAMANHO_BLOCO * 2:
                    esqueleto.saúde -= 50


class Explosão(pygame.sprite.Sprite):
    def __init__(self, x, y, escala):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(0, 4):
            img = pygame.image.load(
                f'recursos/img/explosão/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(
                img, (int(img.get_width() * escala), int(img.get_height() * escala)))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.contador = 0

    def update(self):
        # SCROLLA
        self.rect.x += tela_scroll
        VELOCIDADE_EXPLOSÃO = 4
        # ATUALIZA A ANIMAÇÃO DA EXPLOSÃO
        self.contador += 1
        if self.contador >= VELOCIDADE_EXPLOSÃO:
            self.contador = 0
            self.index += 1
            # SE A ANIMAÇÃO É COMPLETA ENTÃO DELETAA A EXPLOSÃO
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]


class TransicaoTela():
    def __init__(self, direção, cor, velocidade):
        self.direção = direção
        self.cor = cor
        self.velocidade = velocidade
        self.contador_transição = 0

    def transicao(self):
        transicao_completa = False
        self.contador_transição += self.velocidade
        if self.direção == 1:
            pygame.draw.rect(
                tela, self.cor, (0 - self.contador_transição, 0, largura_tela // 2, altura_tela))
            pygame.draw.rect(tela, self.cor, (largura_tela // 2 +
                             self.contador_transição, 0, largura_tela, altura_tela))
            pygame.draw.rect(
                tela, self.cor, (0, 0 - self.contador_transição, largura_tela, altura_tela // 2))
            pygame.draw.rect(tela, self.cor, (0, altura_tela // 2 +
                             self.contador_transição, largura_tela, altura_tela))
        if self.direção == 2:
            pygame.draw.rect(
                tela, self.cor, (0, 0, largura_tela, 0 + self.contador_transição))
        if self.contador_transição >= largura_tela:
            transicao_completa = True

        return transicao_completa



# Classe para o efeito de partículas (folhas caindo)
class Folha(pygame.sprite.Sprite):
    def __init__(self, largura_tela, altura_tela, imagem):
        super().__init__()
        
        # Guarda a imagem original para rotações de qualidade
        self.original_image = imagem
        self.image = self.original_image.copy()
        
        # Posição inicial aleatória (começa fora da tela, no topo)
        self.rect = self.image.get_rect(
            center=(random.randint(0, largura_tela), random.randint(-100, -50))
        )

        # Guarda as posições como floats para um movimento mais suave
        self.pos_x = float(self.rect.centerx)
        self.pos_y = float(self.rect.centery)

        # Propriedades de movimento aleatórias para cada folha
        self.velocidade_y = random.uniform(0.8, 2.5)  # Velocidade de queda
        self.velocidade_x = random.uniform(-0.5, 0.5) # "Balanço" lateral
        self.velocidade_rotacao = random.uniform(-1, 1) # Velocidade de rotação
        self.angulo = 0

        # Referências às dimensões da tela para saber quando resetar
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela

    def rotacionar(self):
        """ Gira a folha e atualiza seu rect para manter o centro."""
        self.angulo = (self.angulo + self.velocidade_rotacao) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angulo)
        self.rect = self.image.get_rect(center=(self.pos_x, self.pos_y))

    def update(self):
        """ Atualiza a posição e rotação da folha a cada frame."""
        # Aplica o movimento
        self.pos_y += self.velocidade_y
        self.pos_x += self.velocidade_x
        
        # Aplica a rotação
        self.rotacionar()

        # Se a folha saiu da parte de baixo da tela, reseta sua posição no topo
        if self.rect.top > self.altura_tela:
            self.pos_y = float(random.randint(-100, -50))
            self.pos_x = float(random.randint(0, self.largura_tela))


# CRIA A TRANSICAO DA TELA
intro_transicao = TransicaoTela(1, preto, 4)
transicao_morte = TransicaoTela(2, ROSA, 4)

# CRIA BOTÕES NO MENU PAUSE

voltar_button = button.Button(largura_tela // 2 - 25,
                              altura_tela // 2 - 70, voltar_img, 1)
sair_button = button.Button(largura_tela // 2,
                            altura_tela // 2 + 40, sair_img, 1)
pause_background_button = button.Button(largura_tela // 2 - 100,
                                        altura_tela // 2 - 150, voltar_img, 1)


# CRIA BOTÕES NO MENU
play_button = button.Button(largura_tela // 2 - 100,
                            altura_tela // 2 - 150, play_img, 1)
exit_button = button.Button(largura_tela // 2 - 8,
                            altura_tela // 2 - 30, exit_img, 1)
restart_button = button.Button(
    largura_tela // 2 - 90, altura_tela // 2 - 20, restart_img, 2)


# CRIA GRUPOS DE SPRITE
grupo_esqueleto = pygame.sprite.Group()
grupo_flecha = pygame.sprite.Group()
grupo_granada = pygame.sprite.Group()
grupo_explosão = pygame.sprite.Group()
grupo_caixas_itens = pygame.sprite.Group()
grupo_decoracao = pygame.sprite.Group()
grupo_agua = pygame.sprite.Group()
grupo_saida = pygame.sprite.Group()
grupo_saida = pygame.sprite.Group()
grupo_folhas = pygame.sprite.Group()
for _ in range(50):
    folha = Folha(largura_tela, altura_tela, folha_img)
    grupo_folhas.add(folha)


# CRIA LISTA VAZIA DE GRADES
world_data = []
for linha in range(linhas):
    r = [-1] * colunas
    world_data.append(r)

# CARREGA OS DADOS DO NIVEL E CRIA O MUNDO
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, linha in enumerate(reader):
        for y, grade in enumerate(linha):
            world_data[x][y] = int(grade)
world = World()
jogador, barra_vida = world.processar_dados(world_data)

# carrega os dados de um nivel e cria o mundo
velocidade_pulso = 0.007
escala_min = 0.8
escala_max = 1



iniciar = True
while iniciar:
    fps.tick(60)
    if iniciar_jogo == False:
        # desenha o menu
        tela.fill(BG)

        if menu_estado == "pedir_nome":
            #  PERGUNTA O NOME
            tela.fill(BG)  # Limpa a tela
            desenhar_texto("O Coronel quer saber seu nome de guerra...",
                           font, branco, largura_tela // 2 - 250, altura_tela // 2 - 50)
            pygame.display.update()  # Mostra a mensagem ANTES de falar

            # A função de fala bloqueia o jogo, por isso atualizamos a tela antes
            falar("Você perdeu seu nome, história, conquistas, agora as únicas coisas que te restam é seu fuzil, teu gorro enumerado e teu nome de guerra.")

            # --- Etapa 2: Avisa que está ouvindo ---
            tela.fill(BG)
            desenhar_texto("Diga seu nome de guerra agora!", font,
                           vermelho, largura_tela // 2 - 180, altura_tela // 2 - 50)
            desenhar_texto("(Microfone ativo)", font, branco,
                           largura_tela // 2 - 120, altura_tela // 2)
            pygame.display.update()  # Mostra "Ouvindo..." ANTES de escutar

            # A função de escuta também bloqueia o jogo
            nome_reconhecido = ouvir()

            # --- Etapa 3: Processa o resultado ---
            if nome_reconhecido:
                nome_jogador = nome_reconhecido
                falar(f"Entendido. Boa sorte no front, {nome_jogador}!")
            else:
                nome_jogador = "Recruta"  # Nome padrão se a fala falhar
                falar(
                    "Não consegui te ouvir bem. Vamos te chamar de Recruta por enquanto.")

            # --- Etapa 4: Muda para o menu principal ---
            menu_estado = "menu"
            pygame.mixer.music.load(
                'recursos/audios/Saudades De Minha Terra.wav')
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1, 0.0, 5000)

        elif menu_estado == "menu":
            # --- SEU MENU PRINCIPAL NORMAL VAI AQUI ---
            desenhar_texto(
                f"Bem-vindo, {nome_jogador}!", font, branco, 400, 150)
            desenhar_texto('Teclas AWSD para se movimentar',
                           font, branco, 350, 380)
            desenhar_texto('Teclado ESPAÇO para atirar',
                           font, branco, 350, 410)
            desenhar_texto('Teclado Q para atirar granada',
                           font, branco, 350, 440)
        # ADICIONA OS BOTÕES NA TELA
            if play_button.draw(tela):
                iniciar_jogo = True
                iniciar_intro = True
            if exit_button.draw(tela):
                iniciar = False

    else:
        if not jogo_pausado:
            tela_background()
            grupo_folhas.update()
            grupo_folhas.draw(tela)
            world.draw()
            
            image_center_pos = (950, 60)
            time_in_ms = pygame.time.get_ticks()
            oscilar = (math.sin(time_in_ms * velocidade_pulso)+1) / 2
            escala_atual = escala_min + (escala_max - escala_min) * oscilar
            nova_largura = int(cobra_fuma.get_width() * escala_atual)
            nova_altura = int(cobra_fuma.get_height() * escala_atual)
            if nova_largura <= 0: nova_largura = 1
            if nova_altura <= 0: nova_altura = 1
            cobra_fuma_redimensionada = pygame.transform.scale(cobra_fuma, (nova_largura, nova_altura))
            cobra_fuma_rect = cobra_fuma_redimensionada.get_rect(center=image_center_pos)
            tela.blit(cobra_fuma_redimensionada, cobra_fuma_rect)
            desenhar_texto(f'PONTOS: {pontos}', font, branco, 10, 95)
            # MOSTRA VIDA DO JOGADOR
            barra_vida.desenhar(jogador.saúde)

            # MOSTRA AS MUNIÇÕES RESTANTES
            desenhar_texto('MUNIÇÕES: ', font, branco, 10, 35)
            for x in range(jogador.munição):
                tela.blit(imagem_flecha, (135 + (x * 10), 40))

            desenhar_texto('GRANADAS: ', font, branco, 10, 65)
            for x in range(jogador.granadas):
                tela.blit(imagem_granada, (145 + (x * 15), 65))

            desenhar_texto('Press Esc to Pause', font, branco, 425, 10)

            jogador.update()
            jogador.desenhar()

            for esqueleto in grupo_esqueleto:
                esqueleto.ia()
                esqueleto.update()
                esqueleto.desenhar()

            # ATUALIZA E DESENHA GRUPOS
            grupo_flecha.update()
            grupo_granada.update()
            grupo_explosão.update()
            grupo_caixas_itens.update()
            grupo_agua.update()
            grupo_decoracao.update()
            grupo_saida.update()

            grupo_flecha.draw(tela)
            grupo_granada.draw(tela)
            grupo_explosão.draw(tela)
            grupo_caixas_itens.draw(tela)
            grupo_agua.draw(tela)
            grupo_decoracao.draw(tela)
            grupo_saida.draw(tela)

            # MOSTRA A INTRO
            if iniciar_intro == True:
                if intro_transicao.transicao():
                    iniciar_intro = False
                    intro_transicao.contador_transição = 0

            # ATUALIZA AÇÃO DO JOGADOR
            if jogador.vida:
                if atirando and not jogador.atacando:
                    jogador.Atacar()
                    atirando = False
                # LANÇAR GRANADA
                elif granada and granada_atirar == False and jogador.granadas > 0:
                    granada = Granada(jogador.rect.centerx + (0.5 * jogador.rect.size[0] * jogador.direção),
                                      jogador.rect.top, jogador.direção)
                    grupo_granada.add(granada)
                    # REDUZ QTD GRANADAS
                    jogador.granadas -= 1
                    granada_atirar = True
                    print(jogador.granadas)
                if jogador.no_ar:
                    jogador.atualizar_ações(2)  # pulo

                elif andar_esquerda or andar_direita:
                    jogador.atualizar_ações(1)  # CORRE

                else:
                    jogador.atualizar_ações(0)  # IDLE - PARADO
                tela_scroll, level_complete = jogador.movimentação(
                    andar_esquerda, andar_direita)
                bg_scroll -= tela_scroll
                # CHECA SE O JOGADOR COMPLETOU O NIVEL
                if level_complete:
                    iniciar_intro = True
                    level += 1
                    bg_scroll = 0
                    world_data = reiniciar_nivel()
                    if level <= MAX_LEVELS:
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, linha in enumerate(reader):
                                for y, grade in enumerate(linha):
                                    world_data[x][y] = int(grade)
                        world = World()
                        jogador, barra_vida = world.processar_dados(world_data)

            else:
                if menu_estado == 'morto':
                    if not log_salvo_nesta_vida:
                        salvar_log(nome_jogador, pontos)
                        ranking_da_partida = obter_ranking()
                        log_salvo_nesta_vida = True

                    tela_scroll = 0
                    if transicao_morte.transicao():
                        desenhar_ranking(
                            ranking_da_partida, largura_tela // 2 - 160, altura_tela // 2 + 50)
                        if restart_button.draw(tela):
                            pontos = 0
                            transicao_morte.contador_transição = 0
                            bg_scroll = 0
                            world_data = reiniciar_nivel()
                            # CARREGA OS DADOS DO NIVEL E CRIA O MUNDO
                            with open(f'level{level}_data.csv', newline='') as csvfile:
                                reader = csv.reader(csvfile, delimiter=',')
                                for x, linha in enumerate(reader):
                                    for y, grade in enumerate(linha):
                                        world_data[x][y] = int(grade)
                            world = World()
                            jogador, barra_vida = world.processar_dados(
                                world_data)

        else:
            tela.blit(pause_background, (400, 200))
            if voltar_button.draw(tela):
                jogo_pausado = False
            if sair_button.draw(tela):
                iniciar = False

    for evento in pygame.event.get():
        # SAIR DO JOGO
        if evento.type == pygame.QUIT:
            iniciar = False
            pygame.quit()
        # TECLAS DE ATALHO PRESSIONADOS
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_a:
                andar_esquerda = True
            if evento.key == pygame.K_d:
                andar_direita = True
            if evento.key == pygame.K_w and jogador.vida:
                jogador.pulo = True
                som_pulo.play()
            if evento.key == pygame.K_ESCAPE:
                jogo_pausado = not jogo_pausado
            if evento.key == pygame.K_SPACE:
                jogador.Atacar()
                atirando = True
            if evento.key == pygame.K_q:
                granada = True

        # EVENTO PARA QUANDO O JOGADOR SOLTA A TECLA
        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_a:
                andar_esquerda = False
            if evento.key == pygame.K_d:
                andar_direita = False
            if evento.key == pygame.K_SPACE:
                jogador.Atacar()
                atirando = False
            if evento.key == pygame.K_q:
                granada = False
                granada_atirar = False

    pygame.display.update()
