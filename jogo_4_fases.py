import pygame
import sys
import math

# ============================================================
# ROBO: FUGA DA ESTACAO
# Plataforma 2D com quatro fases.
# Controles: A/D ou setas = mover | W/ESPACO/SETA CIMA = pular
# R = reiniciar a fase | ESC = sair
# ============================================================

pygame.init()
LARGURA, ALTURA = 960, 544
TILE = 32
FPS = 60
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robo: Fuga da Estacao")
RELOGIO = pygame.time.Clock()
FONTE = pygame.font.SysFont("consolas", 20, bold=True)
FONTE_GRANDE = pygame.font.SysFont("consolas", 42, bold=True)

# Carrega as imagens que acompanham o projeto.
ROBO_IMG = pygame.image.load("player.png").convert_alpha()
TILESET = pygame.image.load("tileset.png").convert_alpha()

# Cada fase é uma matriz de caracteres:
# # plataforma/parede | ^ espinhos | E inimigo | C energia
# P início do robô | D porta de saída | . espaço vazio
FASES = [
[
"..............................",
"..............................",
"...............C..............",
"...........#######............",
"..............................",
".....C..............E.........",
"....####...........####.......",
"..............................",
"...........C..................",
".......#######...........D....",
"..............................",
"..P..............E............",
"########....########....#######",
"##############################",
"##############################",
"##############################",
],
[
"..............................",
"..............................",
"....C.................C.......",
"..#####...........########.....",
"..............................",
"...........E..................",
"......#######.....####.........",
"..............................",
"..................C...........",
"....####......#######......D...",
"..............................",
"P........E.....................",
"########....^^^^....###########",
"##############################",
"##############################",
"##############################",
],
[
"..............................",
"..............................",
"........C.....................",
".....######.......####.........",
"..............................",
"..E.............C..............",
"#####......########......###...",
"..............................",
"...........^^^^.................",
".......#######.........C........",
"...........................D....",
"P.............E.................",
"######...#########...^^^^...#####",
"##############################",
"##############################",
"##############################",
],
[
"..............................",
"..............................",
"..C.............C..............",
"#####.......########............",
"..............................",
"........E..............E.......",
"....#######......#######.........",
"..............................",
".............^^^^...............",
"....C....#######.................",
".............................D..",
"P..............E.................",
"####...^^^^...########...^^^^...##",
"##############################",
"##############################",
"##############################",
]
]

# Corrige eventuais espaços para que todas as linhas tenham 30 colunas.
FASES = [[linha[:30].ljust(30, ".") for linha in fase] for fase in FASES]

def recorte(imagem, x, y, largura, altura):
    area = pygame.Rect(x, y, largura, altura)
    return imagem.subsurface(area).copy()

# Sprites do robô: a folha tem quadros distribuídos em duas linhas.
# São recortados quadrados de 32x32 para preservar a arte original.
ROBO_FRAMES = []
for x in [0, 32, 64, 96, 128, 160, 192, 224]:
    ROBO_FRAMES.append(recorte(ROBO_IMG, x, 32, 32, 32))
if not any(p.get_width() for p in ROBO_FRAMES):
    ROBO_FRAMES = [recorte(ROBO_IMG, 0, 0, 32, 32)]

# Recortes decorativos do tileset (plataforma e espinhos).
# Se um recorte não ficar disponível por diferença no arquivo, o jogo
# continua usando os desenhos geométricos de segurança.
try:
    BLOCO_IMG = recorte(TILESET, 0, 128, 48, 32)
    BLOCO_IMG = pygame.transform.scale(BLOCO_IMG, (TILE, TILE))
except Exception:
    BLOCO_IMG = None

try:
    ESPINHO_IMG = recorte(TILESET, 128, 64, 160, 16)
    ESPINHO_IMG = pygame.transform.scale(ESPINHO_IMG, (TILE, TILE))
except Exception:
    ESPINHO_IMG = None

def texto(tela, mensagem, x, y, cor=(240, 245, 255), fonte=FONTE):
    tela.blit(fonte.render(mensagem, True, cor), (x, y))

class Robo:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 5, y + 3, 22, 28)
        self.vx = 0
        self.vy = 0
        self.no_chao = False
        self.vidas = 3
        self.pontos = 0
        self.energia = 0
        self.invencivel = 0
        self.frame = 0
        self.virado = 1

    def atualizar(self, teclas, blocos):
        self.vx = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vx = -4
            self.virado = -1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vx = 4
            self.virado = 1

        if (teclas[pygame.K_SPACE] or teclas[pygame.K_UP] or teclas[pygame.K_w]) and self.no_chao:
            self.vy = -11
            self.no_chao = False

        self.vy += 0.55
        if self.vy > 12:
            self.vy = 12

        self.rect.x += self.vx
        for bloco in blocos:
            if self.rect.colliderect(bloco):
                if self.vx > 0:
                    self.rect.right = bloco.left
                elif self.vx < 0:
                    self.rect.left = bloco.right

        self.rect.y += int(self.vy)
        self.no_chao = False
        for bloco in blocos:
            if self.rect.colliderect(bloco):
                if self.vy > 0:
                    self.rect.bottom = bloco.top
                    self.no_chao = True
                elif self.vy < 0:
                    self.rect.top = bloco.bottom
                self.vy = 0

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(LARGURA, self.rect.right)
        if self.invencivel > 0:
            self.invencivel -= 1
        if self.vx != 0:
            self.frame += 1

    def desenhar(self, tela):
        quadro = ROBO_FRAMES[(self.frame // 7) % len(ROBO_FRAMES)]
        quadro = pygame.transform.scale(quadro, (34, 34))
        if self.virado < 0:
            quadro = pygame.transform.flip(quadro, True, False)
        if self.invencivel == 0 or (self.invencivel // 5) % 2 == 0:
            tela.blit(quadro, (self.rect.x - 6, self.rect.y - 4))

class Inimigo:
    def __init__(self, x, y, tipo):
        self.rect = pygame.Rect(x + 3, y + 7, 26, 24)
        self.tipo = tipo
        self.vel = 1.7 if tipo == 0 else 2.5
        self.direcao = 1
        self.base_x = x
        self.anim = 0

    def atualizar(self):
        self.anim += 1
        self.rect.x += int(self.vel * self.direcao)
        if self.rect.x < self.base_x - 75 or self.rect.x > self.base_x + 75:
            self.direcao *= -1

    def desenhar(self, tela):
        sobe = 2 if (self.anim // 8) % 2 == 0 else -2
        if self.tipo == 0:
            pygame.draw.rect(tela, (245, 70, 75),
                             (self.rect.x, self.rect.y + sobe, 26, 23), border_radius=6)
            pygame.draw.circle(tela, (255, 255, 255), (self.rect.centerx, self.rect.centery), 4)
        else:
            pygame.draw.circle(tela, (170, 80, 255), self.rect.center, 13 + (self.anim // 10) % 2)
            pygame.draw.circle(tela, (255, 255, 255), (self.rect.centerx + 3, self.rect.centery), 4)

class Fase:
    def __init__(self, numero):
        self.numero = numero
        self.blocos = []
        self.espinhos = []
        self.cristais = []
        self.inimigos = []
        self.porta = None
        self.inicio = (40, 350)
        self.carregar(FASES[numero - 1])

    def carregar(self, matriz):
        for y, linha in enumerate(matriz):
            for x, simbolo in enumerate(linha):
                px, py = x * TILE, y * TILE
                if simbolo == "#":
                    self.blocos.append(pygame.Rect(px, py, TILE, TILE))
                elif simbolo == "^":
                    self.espinhos.append(pygame.Rect(px + 2, py + 9, TILE - 4, TILE - 9))
                elif simbolo == "C":
                    self.cristais.append(pygame.Rect(px + 8, py + 8, 16, 16))
                elif simbolo == "E":
                    self.inimigos.append(Inimigo(px, py, len(self.inimigos) % 2))
                elif simbolo == "P":
                    self.inicio = (px, py)
                elif simbolo == "D":
                    self.porta = pygame.Rect(px + 3, py - 8, 26, 40)

    def desenhar(self, tela):
        tela.fill((9, 13, 29))
        # Fundo sci-fi estrelado.
        for i in range(45):
            x = (i * 97 + self.numero * 31) % LARGURA
            y = (i * 53) % 430
            pygame.draw.circle(tela, (45, 60, 92), (x, y), 1)

        for bloco in self.blocos:
            if BLOCO_IMG:
                tela.blit(BLOCO_IMG, bloco)
            else:
                pygame.draw.rect(tela, (47, 62, 91), bloco)
                pygame.draw.rect(tela, (91, 125, 170), bloco, 2)

        for espinho in self.espinhos:
            if ESPINHO_IMG:
                tela.blit(ESPINHO_IMG, (espinho.x, espinho.y - 8))
            else:
                pygame.draw.polygon(tela, (255, 80, 80),
                    [(espinho.left, espinho.bottom), (espinho.centerx, espinho.top),
                     (espinho.right, espinho.bottom)])

        for cristal in self.cristais:
            pygame.draw.circle(tela, (40, 230, 255), cristal.center, 9)
            pygame.draw.circle(tela, (210, 255, 255), cristal.center, 3)

        if self.porta:
            pygame.draw.rect(tela, (30, 220, 130), self.porta, border_radius=5)
            pygame.draw.rect(tela, (190, 255, 220), self.porta, 2, border_radius=5)

        for inimigo in self.inimigos:
            inimigo.desenhar(tela)

def criar_jogador(fase, vidas=3, pontos=0):
    robo = Robo(*fase.inicio)
    robo.vidas = vidas
    robo.pontos = pontos
    return robo

fase_numero = 1
fase = Fase(fase_numero)
robo = criar_jogador(fase)
estado = "jogando"
mensagem = ""

def reiniciar_fase():
    global fase, robo, estado
    fase = Fase(fase_numero)
    robo = criar_jogador(fase, robo.vidas, robo.pontos)
    estado = "jogando"

def perder_vida():
    global estado
    robo.vidas -= 1
    robo.pontos = max(0, robo.pontos - 15)
    if robo.vidas <= 0:
        estado = "derrota"
    else:
        robo.rect.topleft = (fase.inicio[0] + 5, fase.inicio[1] + 3)
        robo.vy = 0
        robo.invencivel = 100

while True:
    RELOGIO.tick(FPS)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if evento.key == pygame.K_r and estado in ("derrota", "vitoria"):
                fase_numero = 1
                fase = Fase(1)
                robo = criar_jogador(fase)
                estado = "jogando"
            if evento.key == pygame.K_r and estado == "jogando":
                reiniciar_fase()

    if estado == "jogando":
        teclas = pygame.key.get_pressed()
        robo.atualizar(teclas, fase.blocos)

        for inimigo in fase.inimigos:
            inimigo.atualizar()
            if robo.rect.colliderect(inimigo.rect) and robo.invencivel == 0:
                perder_vida()

        for espinho in fase.espinhos:
            if robo.rect.colliderect(espinho) and robo.invencivel == 0:
                perder_vida()

        for cristal in fase.cristais[:]:
            if robo.rect.colliderect(cristal):
                fase.cristais.remove(cristal)
                robo.pontos += 10
                robo.energia += 1

        if robo.rect.top > ALTURA:
            perder_vida()

        if fase.porta and robo.rect.colliderect(fase.porta) and len(fase.cristais) == 0:
            if fase_numero < 4:
                robo.pontos += 50
                fase_numero += 1
                fase = Fase(fase_numero)
                robo = criar_jogador(fase, robo.vidas, robo.pontos)
            else:
                robo.pontos += 100
                estado = "vitoria"

    fase.desenhar(TELA)
    robo.desenhar(TELA)

    pygame.draw.rect(TELA, (8, 10, 20), (0, 480, LARGURA, 64))
    texto(TELA, f"FASE {fase_numero}/4", 18, 490, (90, 225, 255))
    texto(TELA, f"VIDAS: {robo.vidas}", 190, 490)
    texto(TELA, f"PONTOS: {robo.pontos}", 350, 490)
    texto(TELA, f"ENERGIA: {robo.energia}", 570, 490)
    texto(TELA, "A/D ou SETAS: mover | ESPACO: pular | R: reiniciar", 18, 518, (165, 185, 215), pygame.font.SysFont("consolas", 14))

    if estado in ("derrota", "vitoria"):
        camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        camada.fill((0, 0, 0, 190))
        TELA.blit(camada, (0, 0))
        titulo = "VOCE VENCEU!" if estado == "vitoria" else "FIM DE JOGO"
        subtitulo = f"Pontuacao final: {robo.pontos}"
        texto(TELA, titulo, 300, 205, (255, 230, 100), FONTE_GRANDE)
        texto(TELA, subtitulo, 385, 265)
        texto(TELA, "Pressione R para jogar novamente ou ESC para sair", 245, 315, (210, 220, 240))

    pygame.display.flip()
