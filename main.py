import pgzrun
import random

""" CONFIGURATION """

WIDTH = 1024 - 64
HEIGHT = 1024 - 64

TITLE = "Snake game"
ICON = "images/snake_head.png"

""" VARIABLES """
head = Actor("snake_head.png")
head.game_status = "menu"  # Status gry

snake = []  # Lista wszystkich elementów węża

bonus = []  # Lista bonusów

elements = []  # Lista wszystkich elementów gry (poza wężem)

ball = Actor("ball1.png")

start_button = Actor("button1.png")
start_button.x = WIDTH / 2
start_button.y = 200

""" DRAW """


def draw():
    if head.game_status == "game":
        screen.blit("snake_bg.png", (0, 0))

        # Rysujemy wszystkie elementy ciała węża
        for el in snake:
            el.draw()

        head.draw()

        for el in elements:  # Rysujemy wszystkie elementy
            el.draw()

        screen.draw.text(str(head.points), (15, 15), fontsize=60, color="black")

        if head.dead:
            screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2), fontsize=100, color="red")

    if head.game_status == "menu":
        screen.fill("black")
        screen.draw.text("MENU", center=(WIDTH / 2, 50), fontsize=100, color="white")
        start_button.draw()
        screen.draw.text("START", center=(WIDTH / 2, 200), fontsize=50, color="black")


""" UPDATE """


def update():
    if head.game_status == "menu" or head.dead:
        return

    head.frame += 1
    if head.frame >= head.speed:
        head.frame = 0
    else:
        return

    for i in range(len(snake) - 1, 0, -1):
        body = snake[i]

        if body.wait:
            body.wait = False
        else:

            previous = snake[i - 1]
            body.x = previous.x
            body.y = previous.y

    head.x += head.vx
    head.y += head.vy

    if head.x > WIDTH:
        head.x = 32
    if head.x < 0:
        head.x = WIDTH - 32
    if head.y > HEIGHT:
        head.y = 32
    if head.y < 0:
        head.y = HEIGHT - 32

    head_collides_body()

    update_ball_collision()

    for el in elements[:]:
        if head.colliderect(el):

            if el.element_type == "carrot":

                add_body()
                sounds.pickup.play()
                pick_random_pos(el)

                head.points += 1
                if head.speed > 5:
                    head.speed -= 0.5
            elif el.element_type == "bonus1":

                if len(snake) > 1:
                    snake.pop()

                head.speed -= 1

                elements.remove(el)
            elif el.element_type == "wall":
                head.dead = True
                sounds.lose.play()


def update_ball_collision():
    for index in range(1, len(snake)):
        fragment = snake[index]  #

        if fragment.colliderect(ball):

            while len(snake) > index:  #
                snake.pop()

            break


""" EVENTS """


def on_key_down(key):
    if key == keys.LEFT:
        head.vx = -64
        head.vy = 0
        head.angle = -90
    if key == keys.RIGHT:
        head.vx = 64
        head.vy = 0
        head.angle = 90
    if key == keys.UP:
        head.vx = 0
        head.vy = -64
        head.angle = 180
    if key == keys.DOWN:
        head.vx = 0
        head.vy = 64
        head.angle = 0
    if key == keys.SPACE:
        add_body()


def on_mouse_down(pos):
    if head.game_status == "menu":
        if start_button.collidepoint(pos):
            head.game_status = "game"

    if head.game_status == "game" and head.dead:
        head.game_status = "menu"
        init()


""" HELPERS """


def head_collides_body():
    for i in range(1, len(snake)):
        body = snake[i]
        if head.colliderect(body):
            head.dead = True
            sounds.lose.play()


def add_body():
    body = Actor("snake_body.png")
    body.x = snake[-1].x
    body.y = snake[-1].y
    body.wait = True
    snake.append(body)


def is_in_collision(element):
    for body in snake:
        if element.colliderect(body):
            return True

    for el in elements:
        if el != element and element.colliderect(el):
            return True

    return False


# Dodaje "piłkę" - ruchomą przeszkodę
def add_ball():
    ball.element_type = "wall"
    ball.x = 32
    ball.y = random.randint(0, 14) * 64 + 32
    elements.append(ball)

    ball_move_right()  # Poruszamy piłkę w prawo


def ball_move_left():
    animate(ball, pos=(32, ball.y), duration=5, on_finished=ball_move_right, tween="bounce_start")


def ball_move_right():
    animate(ball, pos=(14 * 64 + 32, ball.y), duration=5, on_finished=ball_move_left)


def add_element(type):
    el = Actor(type)
    el.element_type = type

    pick_random_pos(el)

    elements.append(el)


def pick_random_pos(el):
    el.x = random.randint(0, 14) * 64 + 32
    el.y = random.randint(0, 14) * 64 + 32

    while is_in_collision(el):
        el.x = random.randint(0, 14) * 64 + 32
        el.y = random.randint(0, 14) * 64 + 32


""" INITIALIZATION """


def init():
    head.x = 32 + 8 * 64
    head.y = 32 + 8 * 64
    head.vx = 0
    head.vy = 0
    head.frame = 0  # Zliczamy klatki animacji
    head.points = 0  # Zliczamy punkty gracza
    head.speed = 30  # Im mniejsza wartość, tym szybszy wąż
    head.dead = False  # Czy wąż jest martwy

    snake.clear()  # Czyścimy węża
    snake.append(head)  # Dodajemy głowę węża do listy jego elementów

    bonus.clear()
    elements.clear()

    add_element("carrot")
    add_element("bonus1")

    for _ in range(random.randint(6, 10)):
        add_element("wall")

    add_ball()


init()

music.play("flow")
music.set_volume(0.1)

pgzrun.go()
