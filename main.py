import os
import pygame
import random
import csv
pygame.init()


largura_tela = 1000
altura_tela = 700
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption('Shooter')

# DEFINIÇÕES PARA AÇÕES DO JOGADOR
andar_esquerda = False
andar_direita = False
atirando = False
granada = False
granada_atirar = False

# DEFINE VARIÁVEIS DO JOGO
gravidade = 0.5
TAMANHO_BLOCO = 40
linhas = 16
colunas = 150
TAMANHO_BLOCO = altura_tela // linhas
tipos_textura = 15
level = 1
# Carregar imagens
# GUARDA TEXTURAS NA LISTA
img_list = []
for x in range(tipos_textura):
    img = pygame.image.load(f'img/texturas/{x}.png')
    img = pygame.transform.scale(img, (TAMANHO_BLOCO, TAMANHO_BLOCO))
    img_list.append(img)
# FLECHA
imagem_flecha = pygame.image.load('img/jogador/Flecha/0.png').convert_alpha()
imagem_granada = pygame.image.load('img/granada/granada.png').convert_alpha()
imagem_caixa_cura = pygame.image.load(
    'img/caixa_vida/caixa_vida.png').convert_alpha()
imagem_caixa_municao = pygame.image.load(
    'img/caixa_municao/caixa_municao.png').convert_alpha()
imagem_caixa_granada = pygame.image.load(
    'img/caixa_granada/caixa_granada.png').convert_alpha()

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

# DEFINE A FONTE:
font = pygame.font.SysFont('Futura', 30)


def desenhar_texto(text, font, texto_coluna, x, y):
    imagem_texto = font.render(text, True, texto_coluna)
    tela.blit(imagem_texto, (x, y))


def tela_background():
    tela.fill(BG)
    pygame.draw.line(tela, vermelho, (0, 300), (1000, 300))


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
                f'img/{self.tipo_personagem}/{animação}'))
            for i in range(num_de_imagem):
                personagem = pygame.image.load(
                    f'img/{self.tipo_personagem}/{animação}/{i}.png').convert_alpha()
                personagem = pygame.transform.scale(
                    personagem, (personagem.get_width() * escala, personagem.get_height() * escala))
                lista_temp.append(personagem)
            self.lista_animação.append(lista_temp)

        self.image = self.lista_animação[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.atualizar_animação()
        self.verifica_vida()
        # atualiza cooldown
        if self.flecha_cooldown > 0:
            self.flecha_cooldown -= 1

    def movimentação(self, andar_esquerda, andar_direita):
        # MANIPULAÇÃO DE DIREÇÃO E VELOCIDADE DO PERSONAGEM
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
            self.velocidade_queda = -9
            self.pulo = False
            self.no_ar = True
        personagemY += self.velocidade_queda

        # APLICAR GRAVIDADE
        self.velocidade_queda += gravidade
        if self.velocidade_queda > 10:
            self.velocidade_queda
        personagemY += self.velocidade_queda
        # CHECA A COLISÃO COM O CHÃO
        if self.rect.bottom + personagemY > 300:
            personagemY = 300 - self.rect.bottom
            self.no_ar = False

        # ATUALIZAR A POSIÇÃO DO RETÂNGULO
        self.rect.x += personagemX
        self.rect.y += personagemY

    def Atacar(self):
        if self.flecha_cooldown == 0 and self.munição > 0:
            self.flecha_cooldown = 20
            nova_flecha = Flecha(self.rect.centerx + (
                # MANTEM ATACANDO
                0.6 * self.rect.size[0] * self.direção), self.rect.centery, self.direção)
            grupo_flecha.add(nova_flecha)
            self.munição -= 1

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
        if self.saúde <= 0:
            self.saúde = 0
            self.velocidade = 0
            self.vida = False
            self.atualizar_ações(4)

    def desenhar(self):
        tela.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.lista_obstaculo = []

    def processar_dados(self, dados):
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
                        pass  # AGUA
                    elif grade >= 7 and grade <= 8:
                        pass  # decoração
                    elif grade == 9:  # CRIA O JOGADOR
                        jogador = Cavaleiro(
                            'jogador', x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, 2, 3, 25, 5)
                        barra_vida = BarraVida(
                            10, 10, jogador.saúde, jogador.saúde)
                    elif grade == 10:  # CRIA OS INIMIGOS
                        esqueleto = Cavaleiro(
                            'esqueleto', x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, 1.5, 2, 100, 0)
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
                        pass
        return jogador, barra_vida

    def draw(self):
        for tile in self.lista_obstaculo:
            tela.blit(tile[0], tile[1])



class CaixaItens(pygame.sprite.Sprite):
    def __init__(self, tipo_item, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.tipo_item = tipo_item
        self.image = item_caixas[self.tipo_item]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TAMANHO_BLOCO // 2, y +
                            (TAMANHO_BLOCO - self.image.get_height()))

    def update(self):
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
        self.rect.x += (self.direção * self.velocidade)
        # checa se a flecha ja saiu da tela
        if self.rect.right < 0 or self.rect.left > 800:
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
        self.direção = direção

    def update(self):
        self.velocidade_queda += gravidade
        granada_x = self.direção * self.velocidade
        granada_y = self.velocidade_queda

        # CHECA A COLISÃO DA GRANADA COM O CHÃO
        if self.rect.bottom + granada_y > 300:
            granada_y = 300 - self.rect.bottom
            self.velocidade = 0

        # CHECA SE A GRANADA SAIU DA TELA
        if self.rect.left + granada_x < 0 or self.rect.right + granada_x > 800:
            self.direção *= -1
            granada_x = self.direção * self.velocidade

        # ATUALIZA POSIÇÃO DA GRANADA
        self.rect.x += granada_x
        self.rect.y += granada_y

        # CRONOMETRO PARA EXPLODIR
        self.temporizador -= 1
        if self.temporizador <= 0:
            self.kill()
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
                f'img/explosão/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(
                img, (int(img.get_width() * escala), int(img.get_height() * escala)))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.contador = 0

    def update(self):
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


# CRIA GRUPOS DE SPRITE
grupo_esqueleto = pygame.sprite.Group()
grupo_flecha = pygame.sprite.Group()
grupo_granada = pygame.sprite.Group()
grupo_explosão = pygame.sprite.Group()
grupo_caixas_itens = pygame.sprite.Group()


# CRIA LISTA VAZIA DE GRADES
world_data = []

for linha in range(linhas):
    r = [-1] * colunas
    world_data.append(r)
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, linha in enumerate(reader):
        for y, grade in enumerate(linha):
            world_data[x][y] = int(grade)
world = World()
jogador, barra_vida = world.processar_dados(world_data)

# carrega os dados de um nivel e cria o mundo


iniciar = True
while iniciar:

    tela_background()
    world.draw()

    # MOSTRA VIDA DO JOGADOR
    barra_vida.desenhar(jogador.saúde)
    # MOSTRA AS MUNIÇÕES RESTANTES
    desenhar_texto('MUNIÇÕES: ', font, branco, 10, 35)
    for x in range(jogador.munição):
        tela.blit(imagem_flecha, (135 + (x * 10), 40))
    desenhar_texto('GRANADAS: ', font, branco, 10, 65)
    for x in range(jogador.granadas):
        tela.blit(imagem_granada, (145 + (x * 15), 55))

    jogador.update()
    jogador.desenhar()

    grupo_esqueleto.update()
    grupo_esqueleto.draw(tela)
    for esqueleto in grupo_esqueleto:
        esqueleto.ia()
        esqueleto.update()
        esqueleto.desenhar()

    # ATUALIZA E DESENHA GRUPOS
    grupo_flecha.update()
    grupo_granada.update()
    grupo_explosão.update()
    grupo_caixas_itens.update()

    grupo_flecha.draw(tela)
    grupo_granada.draw(tela)
    grupo_explosão.draw(tela)
    grupo_caixas_itens.draw(tela)

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
            jogador.movimentação(andar_esquerda, andar_direita)
        elif andar_esquerda or andar_direita:
            jogador.atualizar_ações(1)  # CORRE
            jogador.movimentação(andar_esquerda, andar_direita)
        else:
            jogador.atualizar_ações(0)  # IDLE - PARADO
        jogador.movimentação(andar_esquerda, andar_direita)

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
            if evento.key == pygame.K_ESCAPE:
                iniciar = False
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
    fps.tick(60)
    pygame.display.update()
