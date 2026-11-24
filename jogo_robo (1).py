import pygame
import sys
import math
import os

pygame.init()

largura, altura = 960, 544
tile = 32
fps = 60

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("robo: fuga da estacao")
relogio = pygame.time.Clock()

fonte = pygame.font.SysFont("consolas", 20, bold=True)
fonte_pequena = pygame.font.SysFont("consolas", 14)
fonte_grande = pygame.font.SysFont("consolas", 42, bold=True)

vidas_iniciais = 5
gravidade = 0.55
pulo_forca = -12.5
pulos_extras = 1
tolerancia_borda = 7
tolerancia_aperto = 7
raio_serra = 16
vaivem_serra = 32
drone_vaivem = 96
drone_balanco = 8

pasta = os.path.dirname(os.path.abspath(__file__))


def caminho(nome):
    return os.path.join(pasta, nome)


robo_img = pygame.image.load(caminho("player.png")).convert_alpha()
tileset = pygame.image.load(caminho("tileset.png")).convert_alpha()

try:
    fundo_img = pygame.image.load(caminho("fundo.png")).convert()
except Exception:
    fundo_img = None
    print("aviso: fundo.png nao encontrado em", pasta)


fases = [
    [
        "..............................",
        "..............................",
        "...............C..............",
        "...........#######............",
        "..............................",
        ".....C..............E.........",
        "....####...........####.......",
        "...................Z..........",
        "...........C..................",
        ".......#######...........D....",
        "..............................",
        "..P.FF........S..E............",
        "########^^^^########^^^^######",
        "##############################",
        "##############################",
        "##############################",
    ],
    [
        "..............................",
        "..............................",
        "....C.................C.......",
        "..#####...........########....",
        ".................Z............",
        "...........E..................",
        "......#######.....####........",
        "..............................",
        "..................C...........",
        "....####......#######......D..",
        "..............................",
        "P...FF...E...S..........S.....",
        "########^^^^####^^^^##########",
        "##############################",
        "##############################",
        "##############################",
    ],
    [
        "..............................",
        "..............................",
        "........C.....................",
        ".....######.......####........",
        "..............................",
        "..E.............C.............",
        "#####......########......###..",
        ".....................Z........",
        "...........^^^................",
        ".......#######.........C......",
        "...........................D..",
        "P.FF.......S..E.....F.....S...",
        "######^^^######^^^^###^^^#####",
        "##############################",
        "##############################",
        "##############################",
    ],
    [
        "..............................",
        "..............................",
        "..C.............C.............",
        "#####.......########..........",
        "..............Z...............",
        "........E..............E......",
        "....#######......#######......",
        "..............................",
        ".............^^^^.............",
        "....C....#######..............",
        ".............................D",
        "P.........S....E...S..F.......",
        "####^^^^######^^^^######^^^###",
        "##############################",
        "##############################",
        "##############################",
    ],
]

fases = [[linha[:30].ljust(30, ".") for linha in fase] for fase in fases]


def recorte(imagem, x, y, largura, altura):
    area = pygame.Rect(x, y, largura, altura)
    return imagem.subsurface(area).copy()


robo_frames = [recorte(robo_img, x, 32, 32, 32) for x in range(0, 256, 32)]

cor_painel = (22, 23, 49)
cor_painel_linha = (14, 11, 32)
cor_painel_ponto = (40, 44, 71)
verde_claro = (136, 214, 96)
verde_medio = (86, 175, 86)
verde_escuro = (45, 129, 79)
verde_sombra = (19, 68, 63)


def desenhar_bloco(tela, px, py, topo, esquerda, direita):
    pygame.draw.rect(tela, cor_painel, (px, py, tile, tile))
    pygame.draw.rect(tela, cor_painel_linha, (px, py, tile, tile), 1)

    for dx, dy in ((8, 8), (24, 8), (8, 24), (24, 24)):
        pygame.draw.rect(tela, cor_painel_ponto, (px + dx - 1, py + dy - 1, 3, 3))

    if esquerda:
        pygame.draw.rect(tela, verde_medio, (px, py, 2, tile))
        pygame.draw.rect(tela, verde_escuro, (px + 2, py, 2, tile))

    if direita:
        pygame.draw.rect(tela, verde_medio, (px + tile - 2, py, 2, tile))
        pygame.draw.rect(tela, verde_escuro, (px + tile - 4, py, 2, tile))

    if topo:
        pygame.draw.rect(tela, verde_claro, (px, py, tile, 2))
        pygame.draw.rect(tela, verde_medio, (px, py + 2, tile, 2))
        pygame.draw.rect(tela, verde_escuro, (px, py + 4, tile, 2))
        pygame.draw.rect(tela, verde_sombra, (px, py + 6, tile, 2))


try:
    espinho_img = pygame.transform.scale(
        recorte(tileset, 192, 56, 16, 8),
        (tile, tile // 2)
    )
except Exception:
    espinho_img = None


drone_metade = [
    "......KK....",
    ".....KOOK...",
    "....KOOKKKKK",
    "...KOOOKSSSS",
    "..KKKKKKGGGG",
    ".KLLLKGOOOOO",
    ".KLOOKGOKKKK",
    ".KOOOKGOKWWW",
    ".KOOOKGOKWWg",
    ".KDOOKGOKWgg",
    ".KDDOKGOKWWg",
    "..KKKKGOKKKK",
    "...BBK.KGGGG",
    "...bBK..KSSS",
    "....KK..KSWW",
    "........KSWW",
    "........KSSS",
    "........KKKK",
]

drone_cores = {
    "K": (14, 11, 32),
    "O": (214, 118, 52),
    "L": (245, 170, 96),
    "D": (150, 74, 40),
    "G": (205, 200, 190),
    "S": (120, 132, 165),
    "W": (22, 26, 48),
    "g": (150, 235, 80),
    "B": (70, 140, 235),
    "b": (150, 205, 255),
}


def montar_drone():
    quadros = []

    for trocar in (False, True):
        img = pygame.Surface((24, len(drone_metade)), pygame.SRCALPHA)

        for y, metade in enumerate(drone_metade):
            for x, letra in enumerate(metade + metade[::-1]):
                if letra == ".":
                    continue

                if trocar and letra in "Bb":
                    letra = "b" if letra == "B" else "B"

                img.set_at((x, y), drone_cores[letra])

        quadros.append(
            pygame.transform.scale(img, (24 * 2, len(drone_metade) * 2))
        )

    return quadros


drone_frames = montar_drone()


def texto(tela, mensagem, x, y, cor=(240, 245, 255), fonte=fonte):
    tela.blit(fonte.render(mensagem, True, cor), (x, y))


class jogador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 5, y + 3, 22, 28)
        self.vx = 0
        self.vy = 0
        self.no_chao = False
        self.coyote = 0
        self.buffer = 0
        self.pulos_extras = pulos_extras
        self.vidas = vidas_iniciais
        self.pontos = 0
        self.energia = 0
        self.invencivel = 0
        self.frame = 0
        self.virado = 1

    def pedir_pulo(self):
        self.buffer = tolerancia_aperto

    def atualizar(self, teclas, blocos):
        self.vx = 0

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vx = -4
            self.virado = -1

        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vx = 4
            self.virado = 1

        segurando_pulo = (
            teclas[pygame.K_SPACE]
            or teclas[pygame.K_UP]
            or teclas[pygame.K_w]
        )

        if self.no_chao:
            self.coyote = tolerancia_borda
            self.pulos_extras = pulos_extras
        elif self.coyote > 0:
            self.coyote -= 1

        if self.buffer > 0:
            self.buffer -= 1

            if self.coyote > 0:
                self.vy = pulo_forca
                self.coyote = 0
                self.buffer = 0
                self.no_chao = False

            elif self.pulos_extras > 0:
                self.vy = pulo_forca * 0.92
                self.pulos_extras -= 1
                self.buffer = 0

        if self.vy < -5 and not segurando_pulo:
            self.vy = -5

        self.vy += gravidade

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

        for bloco in blocos:
            if self.rect.colliderect(bloco):
                if self.vy > 0:
                    self.rect.bottom = bloco.top
                elif self.vy < 0:
                    self.rect.top = bloco.bottom

                self.vy = 0

        sonda = self.rect.move(0, 1)
        self.no_chao = any(sonda.colliderect(b) for b in blocos) and self.vy >= 0

        if self.no_chao:
            self.vy = 0

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(largura, self.rect.right)

        if self.invencivel > 0:
            self.invencivel -= 1

        if self.vx != 0:
            self.frame += 1

    def desenhar(self, tela):
        quadro = robo_frames[(self.frame // 7) % len(robo_frames)]
        quadro = pygame.transform.scale(quadro, (34, 34))

        if self.virado < 0:
            quadro = pygame.transform.flip(quadro, True, False)

        if self.invencivel == 0 or (self.invencivel // 5) % 2 == 0:
            tela.blit(quadro, (self.rect.x - 6, self.rect.y - 4))


class inimigo:
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
            pygame.draw.rect(
                tela,
                (245, 70, 75),
                (self.rect.x, self.rect.y + sobe, 26, 23),
                border_radius=6
            )
            pygame.draw.circle(
                tela,
                (255, 255, 255),
                (self.rect.centerx, self.rect.centery),
                4
            )
        else:
            pygame.draw.circle(
                tela,
                (170, 80, 255),
                self.rect.center,
                13 + (self.anim // 10) % 2
            )
            pygame.draw.circle(
                tela,
                (255, 255, 255),
                (self.rect.centerx + 3, self.rect.centery),
                4
            )


class drone:
    def __init__(self, px, py, indice):
        self.cx0 = px + tile // 2
        self.cy0 = py + tile
        self.cx = self.cx0
        self.cy = self.cy0
        self.t = indice * 50
        self.rect = pygame.Rect(0, 0, 34, 22)
        self.rect.center = (self.cx, self.cy)

    def atualizar(self):
        self.t += 1
        self.cx = self.cx0 + math.sin(self.t * 0.02) * drone_vaivem
        self.cy = self.cy0 + math.sin(self.t * 0.07) * drone_balanco
        self.rect.center = (int(self.cx), int(self.cy))

    def desenhar(self, tela):
        quadro = drone_frames[(self.t // 6) % 2]
        tela.blit(quadro, (int(self.cx) - 24, int(self.cy) - 18))


class serra:
    def __init__(self, px, py, indice):
        self.cx0 = px + tile // 2
        self.cy = py + tile - raio_serra
        self.cx = self.cx0
        self.t = indice * 70
        self.angulo = 0
        self.rect = pygame.Rect(0, 0, raio_serra * 2 - 10, raio_serra * 2 - 10)
        self.rect.center = (self.cx, self.cy)

    def atualizar(self):
        self.t += 1
        self.angulo = (self.angulo + 9) % 360
        self.cx = self.cx0 + math.sin(self.t * 0.03) * vaivem_serra
        self.rect.center = (int(self.cx), int(self.cy))

    def desenhar(self, tela):
        dentes = 12
        pontos = []

        for i in range(dentes * 2):
            ang = math.radians(self.angulo) + i * math.pi / dentes
            raio = raio_serra if i % 2 == 0 else raio_serra - 6
            pontos.append((
                self.cx + math.cos(ang) * raio,
                self.cy + math.sin(ang) * raio
            ))

        pygame.draw.polygon(tela, (205, 215, 230), pontos)
        pygame.draw.polygon(tela, (110, 125, 150), pontos, 2)

        centro = (int(self.cx), int(self.cy))
        pygame.draw.circle(tela, (230, 70, 80), centro, 7)
        pygame.draw.circle(tela, (60, 70, 95), centro, 3)


class fogo:
    def __init__(self, px, py, indice):
        self.x = px
        self.base = py + tile
        self.t = indice * 13
        self.rect = pygame.Rect(px + 6, py + 10, tile - 12, tile - 10)

    def atualizar(self):
        self.t += 1

    def desenhar(self, tela):
        cx = self.x + tile // 2
        base = self.base

        camadas = [
            ((230, 60, 30), 13, 28),
            ((255, 150, 30), 9, 21),
            ((255, 225, 90), 5, 13)
        ]

        for i, (cor, meia, altura) in enumerate(camadas):
            fase = self.t * 0.35 + i * 1.7
            h = altura * (1 + 0.18 * math.sin(fase))
            bal = math.sin(fase * 0.8) * 3

            pontos = [
                (cx - meia, base),
                (cx - meia * 0.7, base - h * 0.45),
                (cx - meia * 0.2 + bal, base - h * 0.75),
                (cx + bal, base - h),
                (cx + meia * 0.3 + bal, base - h * 0.7),
                (cx + meia * 0.75, base - h * 0.4),
                (cx + meia, base),
            ]

            pygame.draw.polygon(tela, cor, pontos)

        for k in range(2):
            subida = (self.t * 1.4 + k * 18) % 34
            fx = cx + math.sin((self.t + k * 11) * 0.2) * 9

            pygame.draw.circle(
                tela,
                (255, 210, 90),
                (int(fx), int(base - 8 - subida)),
                2
            )


class fase:
    def __init__(self, numero):
        self.numero = numero
        self.blocos = []
        self.espinhos = []
        self.cristais = []
        self.inimigos = []
        self.serras = []
        self.fogos = []
        self.drones = []
        self.porta = None
        self.inicio = (40, 350)

        self.carregar(fases[numero - 1])
        self.cenario = self.montar_cenario()

    def carregar(self, matriz):
        for y, linha in enumerate(matriz):
            for x, simbolo in enumerate(linha):
                px, py = x * tile, y * tile

                if simbolo == "#":
                    self.blocos.append(pygame.Rect(px, py, tile, tile))

                elif simbolo == "^":
                    self.espinhos.append(
                        pygame.Rect(px + 4, py + 18, tile - 8, tile - 18)
                    )

                elif simbolo == "S":
                    self.serras.append(serra(px, py, len(self.serras)))

                elif simbolo == "F":
                    self.fogos.append(fogo(px, py, len(self.fogos)))

                elif simbolo == "Z":
                    self.drones.append(drone(px, py, len(self.drones)))

                elif simbolo == "C":
                    self.cristais.append(pygame.Rect(px + 8, py + 8, 16, 16))

                elif simbolo == "E":
                    self.inimigos.append(
                        inimigo(px, py, len(self.inimigos) % 2)
                    )

                elif simbolo == "P":
                    self.inicio = (px, py)

                elif simbolo == "D":
                    self.porta = pygame.Rect(px + 3, py - 8, 26, 40)

    def montar_cenario(self):
        cenario = pygame.Surface((largura, altura))
        cenario.fill((9, 13, 29))

        if fundo_img:
            cenario.blit(fundo_img, (0, 0))
        else:
            for i in range(45):
                x = (i * 97 + self.numero * 31) % largura
                y = (i * 53) % 430
                pygame.draw.circle(cenario, (45, 60, 92), (x, y), 1)

        celulas = {(b.x // tile, b.y // tile) for b in self.blocos}

        def ocupado(cx, cy):
            if cx < 0 or cx >= 30:
                return True

            return (cx, cy) in celulas

        for cx, cy in celulas:
            desenhar_bloco(
                cenario,
                cx * tile,
                cy * tile,
                topo=not ocupado(cx, cy - 1),
                esquerda=not ocupado(cx - 1, cy),
                direita=not ocupado(cx + 1, cy)
            )

        return cenario

    def desenhar(self, tela):
        tela.blit(self.cenario, (0, 0))

        for espinho in self.espinhos:
            if espinho_img:
                tela.blit(espinho_img, (espinho.x - 4, espinho.y - 2))
            else:
                pygame.draw.polygon(
                    tela,
                    (255, 80, 80),
                    [
                        (espinho.left, espinho.bottom),
                        (espinho.centerx, espinho.top),
                        (espinho.right, espinho.bottom)
                    ]
                )

        for fogo_atual in self.fogos:
            fogo_atual.desenhar(tela)

        for serra_atual in self.serras:
            serra_atual.desenhar(tela)

        for cristal in self.cristais:
            pygame.draw.circle(tela, (40, 230, 255), cristal.center, 9)
            pygame.draw.circle(tela, (210, 255, 255), cristal.center, 3)

        if self.porta:
            pygame.draw.rect(tela, (30, 220, 130), self.porta, border_radius=5)
            pygame.draw.rect(tela, (190, 255, 220), self.porta, 2, border_radius=5)

        for inimigo_atual in self.inimigos:
            inimigo_atual.desenhar(tela)

        for drone_atual in self.drones:
            drone_atual.desenhar(tela)


def criar_jogador(fase_atual, vidas=vidas_iniciais, pontos=0):
    novo_robo = jogador(*fase_atual.inicio)
    novo_robo.vidas = vidas
    novo_robo.pontos = pontos
    return novo_robo


fase_numero = 1
fase_atual = fase(fase_numero)
robo = criar_jogador(fase_atual)
estado = "jogando"


def reiniciar_fase():
    global fase_atual, robo, estado

    fase_atual = fase(fase_numero)
    robo = criar_jogador(fase_atual, robo.vidas, robo.pontos)
    estado = "jogando"


def perder_vida():
    global estado

    robo.vidas -= 1
    robo.pontos = max(0, robo.pontos - 15)

    if robo.vidas <= 0:
        estado = "derrota"
    else:
        robo.rect.topleft = (fase_atual.inicio[0] + 5, fase_atual.inicio[1] + 3)
        robo.vy = 0
        robo.invencivel = 100


teclas_pulo = (pygame.K_SPACE, pygame.K_UP, pygame.K_w)


while True:
    relogio.tick(fps)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if evento.key in teclas_pulo and estado == "jogando":
                robo.pedir_pulo()

            if evento.key == pygame.K_r and estado in ("derrota", "vitoria"):
                fase_numero = 1
                fase_atual = fase(1)
                robo = criar_jogador(fase_atual)
                estado = "jogando"

            elif evento.key == pygame.K_r and estado == "jogando":
                reiniciar_fase()

    if estado == "jogando":
        teclas = pygame.key.get_pressed()
        robo.atualizar(teclas, fase_atual.blocos)

        for inimigo_atual in fase_atual.inimigos:
            inimigo_atual.atualizar()

            if estado == "jogando" and robo.rect.colliderect(inimigo_atual.rect) and robo.invencivel == 0:
                perder_vida()

        for drone_atual in fase_atual.drones:
            drone_atual.atualizar()

            if estado == "jogando" and robo.rect.colliderect(drone_atual.rect) and robo.invencivel == 0:
                perder_vida()

        for espinho in fase_atual.espinhos:
            if estado == "jogando" and robo.rect.colliderect(espinho) and robo.invencivel == 0:
                perder_vida()

        for serra_atual in fase_atual.serras:
            serra_atual.atualizar()

            if estado == "jogando" and robo.rect.colliderect(serra_atual.rect) and robo.invencivel == 0:
                perder_vida()

        for fogo_atual in fase_atual.fogos:
            fogo_atual.atualizar()

            if estado == "jogando" and robo.rect.colliderect(fogo_atual.rect) and robo.invencivel == 0:
                perder_vida()

        for cristal in fase_atual.cristais[:]:
            if robo.rect.colliderect(cristal):
                fase_atual.cristais.remove(cristal)
                robo.pontos += 10
                robo.energia += 1

        if estado == "jogando" and robo.rect.top > altura:
            perder_vida()

        if (
            estado == "jogando"
            and fase_atual.porta
            and robo.rect.colliderect(fase_atual.porta)
            and len(fase_atual.cristais) == 0
        ):
            if fase_numero < 4:
                robo.pontos += 50
                fase_numero += 1
                fase_atual = fase(fase_numero)
                robo = criar_jogador(fase_atual, robo.vidas, robo.pontos)
            else:
                robo.pontos += 100
                estado = "vitoria"

    fase_atual.desenhar(tela)
    robo.desenhar(tela)

    if estado == "jogando" and fase_atual.porta and fase_atual.cristais and robo.rect.colliderect(fase_atual.porta.inflate(40, 40)):
        texto(
            tela,
            f"colete todos os cristais ({len(fase_atual.cristais)} restantes)",
            fase_atual.porta.x - 200,
            fase_atual.porta.y - 30,
            (255, 230, 100),
            fonte_pequena
        )

    if fundo_img is None:
        texto(
            tela,
            "fundo.png nao encontrado: coloque na mesma pasta do jogo",
            18,
            12,
            (255, 200, 90),
            fonte_pequena
        )

    pygame.draw.rect(tela, (8, 10, 20), (0, 480, largura, 64))

    texto(tela, f"fase {fase_numero}/4", 18, 490, (90, 225, 255))
    texto(tela, f"vidas: {robo.vidas}", 190, 490)
    texto(tela, f"pontos: {robo.pontos}", 350, 490)
    texto(tela, f"energia: {robo.energia}", 570, 490)

    texto(
        tela,
        "a/d ou setas: mover | espaco: pular (aperte de novo no ar: pulo duplo) | r: reiniciar",
        18,
        518,
        (165, 185, 215),
        fonte_pequena
    )

    if estado in ("derrota", "vitoria"):
        camada = pygame.Surface((largura, altura), pygame.SRCALPHA)
        camada.fill((0, 0, 0, 190))
        tela.blit(camada, (0, 0))

        titulo = "voce venceu!" if estado == "vitoria" else "fim de jogo"
        subtitulo = f"pontuacao final: {robo.pontos}"

        texto(tela, titulo, 300, 205, (255, 230, 100), fonte_grande)
        texto(tela, subtitulo, 385, 265)
        texto(
            tela,
            "pressione r para jogar novamente ou esc para sair",
            245,
            315,
            (210, 220, 240)
        )

    pygame.display.flip()