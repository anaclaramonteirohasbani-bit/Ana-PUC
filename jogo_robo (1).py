
import pygame
import sys

pygame.init()

largura, altura = 960, 544
tile = 32
fps = 60

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("robo: fuga da estacao")

relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("consolas", 20, bold=True)
fonte_grande = pygame.font.SysFont("consolas", 42, bold=True)

robo_img = pygame.image.load("player.png").convert_alpha()
tileset = pygame.image.load("tileset.png").convert_alpha()

fases = [
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

fases = [[linha[:30].ljust(30, ".") for linha in fase] for fase in fases]


def recorte(imagem, x, y, largura, altura):
    area = pygame.Rect(x, y, largura, altura)
    return imagem.subsurface(area).copy()


quadros_robo = []

for x in [0, 32, 64, 96, 128, 160, 192, 224]:
    quadros_robo.append(recorte(robo_img, x, 32, 32, 32))

bloco_img = None
espinho_img = None

try:
    bloco_img = recorte(tileset, 0, 128, 48, 32)
    bloco_img = pygame.transform.scale(bloco_img, (tile, tile))
except:
    bloco_img = None

try:
    espinho_img = recorte(tileset, 128, 64, 160, 16)
    espinho_img = pygame.transform.scale(espinho_img, (tile, tile))
except:
    espinho_img = None


def mostrar_texto(mensagem, x, y, cor=(240, 245, 255), fonte_usada=fonte):
    imagem = fonte_usada.render(mensagem, True, cor)
    tela.blit(imagem, (x, y))


def criar_robo(x, y, vidas=3, pontos=0):
    robo = {
        "rect": pygame.Rect(x + 5, y + 3, 22, 28),
        "vx": 0,
        "vy": 0,
        "no_chao": False,
        "vidas": vidas,
        "pontos": pontos,
        "energia": 0,
        "invencivel": 0,
        "frame": 0,
        "virado": 1
    }

    return robo


def criar_inimigo(x, y, tipo):
    inimigo = {
        "rect": pygame.Rect(x + 3, y + 7, 26, 24),
        "tipo": tipo,
        "vel": 1.7 if tipo == 0 else 2.5,
        "direcao": 1,
        "base_x": x,
        "anim": 0
    }

    return inimigo


def criar_fase(numero):
    fase = {
        "numero": numero,
        "blocos": [],
        "espinhos": [],
        "cristais": [],
        "inimigos": [],
        "porta": None,
        "inicio": (40, 350)
    }

    matriz = fases[numero - 1]

    for y, linha in enumerate(matriz):
        for x, simbolo in enumerate(linha):
            px = x * tile
            py = y * tile

            if simbolo == "#":
                bloco = pygame.Rect(px, py, tile, tile)
                fase["blocos"].append(bloco)

            elif simbolo == "^":
                espinho = pygame.Rect(px + 2, py + 9, tile - 4, tile - 9)
                fase["espinhos"].append(espinho)

            elif simbolo == "C":
                cristal = pygame.Rect(px + 8, py + 8, 16, 16)
                fase["cristais"].append(cristal)

            elif simbolo == "E":
                tipo = len(fase["inimigos"]) % 2
                inimigo = criar_inimigo(px, py, tipo)
                fase["inimigos"].append(inimigo)

            elif simbolo == "P":
                fase["inicio"] = (px, py)

            elif simbolo == "D":
                fase["porta"] = pygame.Rect(px + 3, py - 8, 26, 40)

    return fase


def atualizar_robo(robo, teclas, blocos):
    rect = robo["rect"]

    robo["vx"] = 0

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
        robo["vx"] = -4
        robo["virado"] = -1

    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
        robo["vx"] = 4
        robo["virado"] = 1

    if (teclas[pygame.K_SPACE] or teclas[pygame.K_UP] or teclas[pygame.K_w]) and robo["no_chao"]:
        robo["vy"] = -11
        robo["no_chao"] = False

    robo["vy"] += 0.55

    if robo["vy"] > 12:
        robo["vy"] = 12

    rect.x += robo["vx"]

    for bloco in blocos:
        if rect.colliderect(bloco):
            if robo["vx"] > 0:
                rect.right = bloco.left

            elif robo["vx"] < 0:
                rect.left = bloco.right

    rect.y += int(robo["vy"])
    robo["no_chao"] = False

    for bloco in blocos:
        if rect.colliderect(bloco):
            if robo["vy"] > 0:
                rect.bottom = bloco.top
                robo["no_chao"] = True

            elif robo["vy"] < 0:
                rect.top = bloco.bottom

            robo["vy"] = 0

    if rect.left < 0:
        rect.left = 0

    if rect.right > largura:
        rect.right = largura

    if robo["invencivel"] > 0:
        robo["invencivel"] -= 1

    if robo["vx"] != 0:
        robo["frame"] += 1


def desenhar_robo(robo):
    quadro = quadros_robo[(robo["frame"] // 7) % len(quadros_robo)]
    quadro = pygame.transform.scale(quadro, (34, 34))

    if robo["virado"] < 0:
        quadro = pygame.transform.flip(quadro, True, False)

    if robo["invencivel"] == 0 or (robo["invencivel"] // 5) % 2 == 0:
        tela.blit(quadro, (robo["rect"].x - 6, robo["rect"].y - 4))


def atualizar_inimigo(inimigo):
    inimigo["anim"] += 1

    rect = inimigo["rect"]
    rect.x += int(inimigo["vel"] * inimigo["direcao"])

    if rect.x < inimigo["base_x"] - 75 or rect.x > inimigo["base_x"] + 75:
        inimigo["direcao"] *= -1


def desenhar_inimigo(inimigo):
    rect = inimigo["rect"]

    sobe = 2 if (inimigo["anim"] // 8) % 2 == 0 else -2

    if inimigo["tipo"] == 0:
        pygame.draw.rect(
            tela,
            (245, 70, 75),
            (rect.x, rect.y + sobe, 26, 23),
            border_radius=6
        )

        pygame.draw.circle(
            tela,
            (255, 255, 255),
            (rect.centerx, rect.centery),
            4
        )

    else:
        pygame.draw.circle(
            tela,
            (170, 80, 255),
            rect.center,
            13 + (inimigo["anim"] // 10) % 2
        )

        pygame.draw.circle(
            tela,
            (255, 255, 255),
            (rect.centerx + 3, rect.centery),
            4
        )


def desenhar_fase(fase):
    tela.fill((9, 13, 29))

    for i in range(45):
        x = (i * 97 + fase["numero"] * 31) % largura
        y = (i * 53) % 430

        pygame.draw.circle(tela, (45, 60, 92), (x, y), 1)

    for bloco in fase["blocos"]:
        if bloco_img:
            tela.blit(bloco_img, bloco)

        else:
            pygame.draw.rect(tela, (47, 62, 91), bloco)
            pygame.draw.rect(tela, (91, 125, 170), bloco, 2)

    for espinho in fase["espinhos"]:
        if espinho_img:
            tela.blit(espinho_img, (espinho.x, espinho.y - 8))

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

    for cristal in fase["cristais"]:
        pygame.draw.circle(tela, (40, 230, 255), cristal.center, 9)
        pygame.draw.circle(tela, (210, 255, 255), cristal.center, 3)

    if fase["porta"]:
        pygame.draw.rect(
            tela,
            (30, 220, 130),
            fase["porta"],
            border_radius=5
        )

        pygame.draw.rect(
            tela,
            (190, 255, 220),
            fase["porta"],
            2,
            border_radius=5
        )

    for inimigo in fase["inimigos"]:
        desenhar_inimigo(inimigo)


def reiniciar_fase():
    global fase, robo, estado

    fase = criar_fase(fase_numero)

    robo = criar_robo(
        fase["inicio"][0],
        fase["inicio"][1],
        robo["vidas"],
        robo["pontos"]
    )

    estado = "jogando"


def perder_vida():
    global estado

    robo["vidas"] -= 1
    robo["pontos"] = max(0, robo["pontos"] - 15)

    if robo["vidas"] <= 0:
        estado = "derrota"

    else:
        robo["rect"].topleft = (
            fase["inicio"][0] + 5,
            fase["inicio"][1] + 3
        )

        robo["vy"] = 0
        robo["invencivel"] = 100


fase_numero = 1
fase = criar_fase(fase_numero)

robo = criar_robo(
    fase["inicio"][0],
    fase["inicio"][1]
)

estado = "jogando"

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

            if evento.key == pygame.K_r and estado in ("derrota", "vitoria"):
                fase_numero = 1
                fase = criar_fase(1)

                robo = criar_robo(
                    fase["inicio"][0],
                    fase["inicio"][1]
                )

                estado = "jogando"

            elif evento.key == pygame.K_r and estado == "jogando":
                reiniciar_fase()

    if estado == "jogando":

        teclas = pygame.key.get_pressed()

        atualizar_robo(robo, teclas, fase["blocos"])

        for inimigo in fase["inimigos"]:
            atualizar_inimigo(inimigo)

            if robo["rect"].colliderect(inimigo["rect"]) and robo["invencivel"] == 0:
                perder_vida()

        for espinho in fase["espinhos"]:
            if robo["rect"].colliderect(espinho) and robo["invencivel"] == 0:
                perder_vida()

        for cristal in fase["cristais"][:]:
            if robo["rect"].colliderect(cristal):
                fase["cristais"].remove(cristal)
                robo["pontos"] += 10
                robo["energia"] += 1

        if robo["rect"].top > altura:
            perder_vida()

        if fase["porta"] and robo["rect"].colliderect(fase["porta"]) and len(fase["cristais"]) == 0:

            if fase_numero < 4:
                robo["pontos"] += 50
                fase_numero += 1

                fase = criar_fase(fase_numero)

                robo = criar_robo(
                    fase["inicio"][0],
                    fase["inicio"][1],
                    robo["vidas"],
                    robo["pontos"]
                )

            else:
                robo["pontos"] += 100
                estado = "vitoria"

    desenhar_fase(fase)
    desenhar_robo(robo)

    pygame.draw.rect(tela, (8, 10, 20), (0, 480, largura, 64))

    mostrar_texto(f"FASE {fase_numero}/4", 18, 490, (90, 225, 255))
    mostrar_texto(f"VIDAS: {robo['vidas']}", 190, 490)
    mostrar_texto(f"PONTOS: {robo['pontos']}", 350, 490)
    mostrar_texto(f"ENERGIA: {robo['energia']}", 570, 490)

    mostrar_texto(
        "A/D ou SETAS: mover | ESPACO: pular | R: reiniciar",
        18,
        518,
        (165, 185, 215),
        pygame.font.SysFont("consolas", 14)
    )

    if estado in ("derrota", "vitoria"):

        camada = pygame.Surface((largura, altura), pygame.SRCALPHA)
        camada.fill((0, 0, 0, 190))

        tela.blit(camada, (0, 0))

        if estado == "vitoria":
            titulo = "VOCE VENCEU!"
        else:
            titulo = "FIM DE JOGO"

        subtitulo = f"Pontuacao final: {robo['pontos']}"

        mostrar_texto(
            titulo,
            300,
            205,
            (255, 230, 100),
            fonte_grande
        )

        mostrar_texto(subtitulo, 385, 265)

        mostrar_texto(
            "Pressione R para jogar novamente ou ESC para sair",
            245,
            315,
            (210, 220, 240)
        )

    pygame.display.flip()
