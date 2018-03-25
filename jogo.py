import pygame, sys, os
import random

# tamanhos
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 680
ARQUEIRO_WIDTH, ARQUEIRO_HEIGHT = 116, 154
DRAGAO_WIDTH, DRAGAO_HEIGHT = 300, 314
FLECHA_WIDTH, FLECHA_HEIGHT = 80, 24
FIREBALL_WIDTH, FIREBALL_HEIGHT = 190, 110
# velocidades
JOGADOR_V = 5
DRAGAO_V = 1
FIREBALL_V = 6
FLECHA_V = 20
# HP
JOGADOR_VIDA = 100
DRAGAO_VIDA = 8000
# DANO no intervalo x-y aleatório
FLECHA_A, FLECHA_B = 90, 110
FIREBALL_A, FIREBALL_B = 10, 15
# posicao de disparo
FLECHA_X, FLECHA_Y = 116, 53
FIREBALL_Y = 102
# cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (34, 139, 34)
BLUE = (135, 206, 250)
BLACK = (0, 0, 0)
# quadro por segundo
FPS = 60
# dicionario de imagens
_image_library = {}
# fim
gameOver = False


def get_image(path):
    # carrega uma imagem no dicionario _image_library
    # caso imagem tenha sido carregada, retorna imagem
    global _image_library
    image = _image_library.get(path)
    if image is None:
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
        image = pygame.image.load(canonicalized_path)
        _image_library[path] = image
    return image


class Arqueiro(pygame.sprite.Sprite):
    width = ARQUEIRO_WIDTH
    height = ARQUEIRO_HEIGHT
    velX = 0
    velY = 0

    def __init__(self, pos, vida, v):
        pygame.sprite.Sprite.__init__(self)
        self.image = get_image("img/arqueiro.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.vida = vida
        self.v = v

    def update(self):
        # calcula a nova posição (x,y)
        self.rect.x += self.velX
        self.rect.y += self.velY

        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if (self.rect.y + self.height) > SCREEN_HEIGHT:
            self.rect.y = SCREEN_HEIGHT - self.height


class Dragao(pygame.sprite.Sprite):
    width = DRAGAO_WIDTH
    height = DRAGAO_HEIGHT
    v = 0

    def __init__(self, pos, vida):
        pygame.sprite.Sprite.__init__(self)
        self.image = get_image("img/dragao.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.vida = vida

    def update(self):
        # calcula a nova posição y
        self.v = 0
        aY = jogador.rect.y
        aYH = jogador.rect.y + jogador.rect.height

        keys = pygame.key.get_pressed()

        if (aY > 0) and (aYH < SCREEN_HEIGHT):
            if keys[pygame.K_UP]:
                self.v = -DRAGAO_V
            if keys[pygame.K_DOWN]:
                self.v = DRAGAO_V
        self.rect.y += self.v


class Flecha(pygame.sprite.Sprite):
    width = FLECHA_WIDTH
    height = FLECHA_HEIGHT

    def __init__(self, pos, v):
        pygame.sprite.Sprite.__init__(self)
        self.image = get_image('img/flecha.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.v = v

    def update(self):
        # calcula a nova posição x
        self.rect.x += self.v
        # remove caso saia da tela
        if self.rect.x-FLECHA_WIDTH > SCREEN_WIDTH:
            self.kill()


class Fireball(pygame.sprite.Sprite):
    width = FIREBALL_WIDTH
    height = FIREBALL_HEIGHT
    velY = 0

    def __init__(self, pos, v):
        pygame.sprite.Sprite.__init__(self)
        self.image = get_image('img/fireball.png')
        self.rect = self.image.get_rect()
        self.velX = v
        self.rect.topleft = pos

    def aim_player(self, a, dx):
        """
        mira bola de fogo no centro do arqueiro
        divide o canvas em 8 partes
        e muda a velocidade Y da bola de fogo
        de acordo com a posição do arqueiro

        a = jogador.rect.y + (ARQUEIRO_HEIGHT/2)
        dX = dragao.rect.x
        """

        c = SCREEN_HEIGHT / 8

        if (a >= 0) and (a <= c) and (self.rect.x == dx):
            self.velY = -4
        elif (a >= c) and (a <= 2*c) and (self.rect.x == dx):
            self.velY = -3
        elif (a >= 2*c) and (a <= 3*c) and (self.rect.x == dx):
            self.velY = -2
        elif (a >= 3*c) and (a <= 4*c) and (self.rect.x == dx):
            self.velY = 0
        elif (a >= 4*c) and (a <= 5*c) and (self.rect.x == dx):
            self.velY = 0
        elif (a >= 5*c) and (a <= 6*c) and (self.rect.x == dx):
            self.velY = 2
        elif (a >= 6*c) and (a <= 7*c) and (self.rect.x == dx):
            self.velY = 3
        elif (a >= 7*c) and (a <= 8*c) and (self.rect.x == dx):
            self.velY = 4

    def aim_random(self):
        self.velY = random.randint(-3, 3)

    def update(self):
        # calcula a nova posição x,y
        self.rect.x += self.velX
        self.rect.y += self.velY
        # remove caso saia da tela e dispara novamente
        if self.rect.x + FIREBALL_WIDTH < 0 or self.rect.y + FIREBALL_HEIGHT < 0 or self.rect.y > SCREEN_HEIGHT:
            self.kill()


class Texto(pygame.sprite.Sprite):
    def __init__(self, pos, text, size, cor_fundo, cor_texto, caixa, xy):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(caixa)
        self.image.fill(cor_fundo)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.font = pygame.font.SysFont("Arial", size)
        self.text = self.font.render(text, 1, cor_texto)
        self.image.blit(self.text, (xy[0], xy[1]))


class Cooldown():
    def __init__(self):
        self.last = pygame.time.get_ticks()
        self.cooldown = 300

    def fire(self):
        # fire gun, only if cooldown has been 0.3 seconds since last
        now = pygame.time.get_ticks()
        if now - self.last >= self.cooldown:
            self.last = now
            # spawn_bullet()


def entrada():
    # verifica pressionamento das teclas
    keys = pygame.key.get_pressed()

    jogador.velX = 0
    jogador.velY = 0
    dragao.velY = 0

    if keys[pygame.K_RIGHT]:
        jogador.velX = jogador.v
    if keys[pygame.K_LEFT]:
        jogador.velX = -jogador.v
    if keys[pygame.K_UP]:
        jogador.velY = -jogador.v
    if keys[pygame.K_DOWN]:
        jogador.velY = jogador.v


def add_flecha():
    tmpflecha = Flecha([jogador.rect.x + FLECHA_X, jogador.rect.y + FLECHA_Y], FLECHA_V)

    flechas_sprites.add(tmpflecha)
    all_sprites.add(tmpflecha)


def add_fireball(v, diff):
    tmpfireball = Fireball([dragao.rect.x, dragao.rect.y + FIREBALL_Y], -(v-diff))
    tmpfireball.aim_player(jogador.rect.y + (ARQUEIRO_HEIGHT/2), dragao.rect.x)

    fireball_sprites.add(tmpfireball)
    all_sprites.add(tmpfireball)


def add_fireball_random(v, diff):
    tmpfireball = Fireball([dragao.rect.x, dragao.rect.y + FIREBALL_Y], -(v-diff))
    tmpfireball.aim_random()

    fireball_sprites.add(tmpfireball)
    all_sprites.add(tmpfireball)


def add_fireball2():
    tmpfireball = Fireball([dragao.rect.x, 50], -FIREBALL_V)
    fireball_sprites.add(tmpfireball)
    all_sprites.add(tmpfireball)

    tmpfireball = Fireball([dragao.rect.x, 300], -FIREBALL_V)
    fireball_sprites.add(tmpfireball)
    all_sprites.add(tmpfireball)

    tmpfireball = Fireball([dragao.rect.x, 550], -FIREBALL_V)
    fireball_sprites.add(tmpfireball)
    all_sprites.add(tmpfireball)


def dispara_fireball():
    if (dragao.vida <= 9000) and (dragao.vida > 8000):
        # uma bola de fogo
        add_fireball(FIREBALL_V, 0)
    elif (dragao.vida <= 8000) and (dragao.vida > 6000):
        # duas bolas de fogo
        add_fireball(FIREBALL_V, 0)
        add_fireball(FIREBALL_V, 2)
    elif (dragao.vida <= 6000) and (dragao.vida > 5000):
        # tres bolas de fogo
        add_fireball(FIREBALL_V, 0)
        add_fireball(FIREBALL_V, 1.5)
        add_fireball(FIREBALL_V, 3)
    elif (dragao.vida <= 5000) and (dragao.vida > 4000):
        # uma bola de fogo aleatoria
        add_fireball_random(FIREBALL_V+1, 0)
    elif (dragao.vida <= 4000) and (dragao.vida > 2000):
        # duas bolas de fogo aleatorias
        add_fireball_random(FIREBALL_V+1, 0)
        add_fireball_random(FIREBALL_V+1, 0)
    elif (dragao.vida <= 2000) and (dragao.vida > 0):
        # tres bolas de fogo aleatorias
        add_fireball_random(FIREBALL_V-1, 0)
        add_fireball_random(FIREBALL_V+1, 0)
        add_fireball_random(FIREBALL_V-1, 0)


def add_texto_score(pos, texto):
    all_sprites.remove(texto_sprites)
    tmptexto = Texto(pos, texto, 52, WHITE, RED, [116, 48], [0, -5])
    texto_sprites.add = tmptexto
    all_sprites.add(tmptexto)


def add_texto_gameover(pos, texto):
    all_sprites.remove(texto_sprites)
    tmptexto = Texto(pos, texto, 52, BLACK, RED, [320, 48], [0, -5])
    texto_sprites.add = tmptexto
    all_sprites.add(tmptexto)

def add_texto_win(pos, texto):
    all_sprites.remove(texto_sprites)
    tmptexto = Texto(pos, texto, 42, BLACK, RED, [430, 48], [5, 0])
    texto_sprites.add = tmptexto
    all_sprites.add(tmptexto)


def colisao():
    # verifica colisao de Sprite
    # salva lista com sprites que colidem e remove objeto que colidiu
    blocks_hit_list1 = pygame.sprite.spritecollide(dragao, flechas_sprites, True)
    blocks_hit_list2 = pygame.sprite.spritecollide(jogador, fireball_sprites, True)

    # muda score para cada objeto que colide
    for block in blocks_hit_list1:
        # modifica score
        dragao.vida += -(random.randint(FLECHA_A, FLECHA_B))
        if dragao.vida < 0:
            dragao.vida = 0
        add_texto_score([715, 5], str(dragao.vida))

    for block in blocks_hit_list2:
        # modifica score
        jogador.vida += -(random.randint(FIREBALL_A, FIREBALL_B))
        if jogador.vida < 0:
            jogador.vida = 0
        add_texto_score([150, 5], str(jogador.vida))


def game_over():
    if jogador.vida <= 0:
        add_texto_gameover([335, 5], 'GAME OVER')
        all_sprites.remove(flechas_sprites)
        all_sprites.remove(fireball_sprites)
        flechas_sprites.empty()
        fireball_sprites.empty()
        jogador.image = get_image("img/arqueiro_queimado.png")
        return True
    elif dragao.vida <= 0:
        add_texto_win([275, 5], 'O DRAGAO MORREU')
        all_sprites.remove(flechas_sprites)
        all_sprites.remove(fireball_sprites)
        flechas_sprites.empty()
        fireball_sprites.empty()
        dragao.image = get_image("img/dragao_morto.png")
        return True
    elif jogador.rect.x + jogador.width >= SCREEN_WIDTH/2:
        add_texto_gameover([335, 5], 'GAME OVER')
        add_texto_score([150, 5], '0')
        all_sprites.remove(flechas_sprites)
        all_sprites.remove(fireball_sprites)
        flechas_sprites.empty()
        fireball_sprites.empty()
        jogador.image = get_image("img/arqueiro_morto.png")
        dragao.rect.topleft = [jogador.rect.x + jogador.width, jogador.rect.y]
        return True

    return False


pygame.init()
pygame.display.set_caption('Arqueiro Vs Dragao')
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

# RenderUpdates Sprite Group
all_sprites = pygame.sprite.RenderUpdates()
flechas_sprites = pygame.sprite.RenderUpdates()
fireball_sprites = pygame.sprite.RenderUpdates()
texto_sprites = pygame.sprite.RenderUpdates()

# add jogador
jogador = Arqueiro([100, 250], JOGADOR_VIDA, JOGADOR_V)
all_sprites.add(jogador)
# add dragao
dragao = Dragao([640, 183], DRAGAO_VIDA)
all_sprites.add(dragao)
# add flecha
add_flecha()
# add fireball
add_fireball(FIREBALL_V, 0)
# add score
add_texto_score([150, 5], str(jogador.vida))
add_texto_score([715, 5], str(dragao.vida))

# desenha imagem do background
background = pygame.image.load('img/background.png').convert()
screen.blit(background, [0, 0])
pygame.display.update()

# eventos do usuario
pygame.time.set_timer(pygame.USEREVENT + 1, 500)
pygame.time.set_timer(pygame.USEREVENT + 2, 2000)

# loop jogo
while True:
    # tratador de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.USEREVENT + 1 and not gameOver:
            # adiciona flecha a cada 500ms
            add_flecha()
        elif event.type == pygame.USEREVENT + 2 and not gameOver:
            # adiciona fireball a cada 2000ms
            dispara_fireball()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                # reinicia jogo ao apertar F5
                pygame.quit()
                os.system('jogo.py')
                sys.exit()

    gameOver = game_over()

    if not gameOver:
        # input do teclado
        entrada()

        # movimenta sprites
        jogador.update()
        dragao.update()
        flechas_sprites.update()
        fireball_sprites.update()

        # detecta colisao (flecha, dragao) e (fireball, jogador) e modifica score
        colisao()

    # desenha o background sobre os sprites
    all_sprites.clear(screen, background)
    # all_sprites.draw retorna uma lista das areas retangulares na tela que mudaram
    rectlist = all_sprites.draw(screen)
    # modifica somente as areas que mudaram
    pygame.display.update(rectlist)
    clock.tick(FPS)
