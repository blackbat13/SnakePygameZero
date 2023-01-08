import pgzrun
import random

WIDTH = 1024 - 64
HEIGHT = 1024 - 64

TITLE = "Snake game"
ICON = "images/snake_head.png"

# Głowa węża
head = Actor("snake_head.png")
head.game_status = "menu"  # Status gry

snake = []  # Lista wszystkich elementów węża

bonus = []  # Lista bonusów

elements = []  # Lista wszystkich elementów gry (poza wężem)

ball = Actor("ball1.png")

start_button = Actor("button1.png")
start_button.x = WIDTH / 2
start_button.y = 200


def initialize():
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

    while el_collides(el):
        el.x = random.randint(0, 14) * 64 + 32
        el.y = random.randint(0, 14) * 64 + 32


# Sprawdzamy, czy element jest w kolizji z czymkolwiek na planszy (wężem, lub innym elementem)
def el_collides(element):
    # Najpierw sprawdzamy, czy element jest w kolizji z wężem
    for body in snake:
        if element.colliderect(body):
            return True

    # Sprawdzamy, czy element jest w kolizji z innym elementem
    for el in elements:
        # Uważamy, żeby nie sprawdzić, czy element jest w kolizji z samym sobą
        if el != element and element.colliderect(el):  # Sprawdzamy, czy jest kolizja
            return True

    return False  # Nie ma kolizji


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


def on_mouse_down(pos):
    if head.game_status == "menu":
        # Jeżeli kliknęliśmy w przycisk start
        if start_button.collidepoint(pos):
            # Zmieniamy stan gry
            head.game_status = "game"

    if head.game_status == "game" and head.dead:
        head.game_status = "menu"
        initialize()


# Sprawdzamy, czy kula koliduje z fragmentem ciała węża (oprócz głowy)
# Jeżeli tak, to obcinamy węża
def check_ball():
    # Przechodzimy przez kolejne fragmenty ciała węża
    for index in range(1, len(snake)):
        # index - numer fragmentu węża w liście snake
        fragment = snake[index]  # Zapamiętujemy w nowej zmiennej fragment ciała węża
        # Sprawdzamy, czy ten fragment ciała węża jest w kolizji z piłką
        if fragment.colliderect(ball):
            # Obcinamy węża!

            while len(snake) > index:  # Dopóki wąż jest za długi
                snake.pop()  # Usuwamy ostatni element węża

            break  # Kończymy


def update():
    # Jeżeli jesteśmy w menu, to nie aktualizujemy gry
    if head.game_status == "menu":
        return

    # Jeżeli koniec gry
    if head.dead:
        return  # To nie atkualizuj gry

    head.frame += 1  # Zwiększamy licznik klatek animacji
    if head.frame >= head.speed:  # Co 30 klatek wykonujemy ruch
        head.frame = 0
    else:
        return  # Jeżeli nie czas na aktualizację, to nic więcej nie robimy

    for i in range(len(snake) - 1, 0, -1):  # Przechodzimy od końca listy z elementami węża
        body = snake[i]  # Dla ułatwienia zapamiętujemy i-ty element węża w zmiennej body
        # Jeżeli element "czeka", to zmieniamy wartość czekania
        if body.wait:
            body.wait = False
        else:
            # Poruszamy elementem - przypisujemy mu pozycję poprzedniego elementu węża
            previous = snake[i - 1]  # Dla ułatwienia zapamiętujemy poprzedni element w nowej zmiennej
            body.x = previous.x
            body.y = previous.y

    head.x += head.vx
    head.y += head.vy

    if head.x > WIDTH:  # Jeżeli wąż wyszedł z prawej strony ekranu
        head.x = 32  # To przemieszczamy go na lewą stronę
    if head.x < 0:
        head.x = WIDTH - 32
    if head.y > HEIGHT:
        head.y = 32
    if head.y < 0:
        head.y = HEIGHT - 32

    # Sprawdzamy, czy wąż zjadł samego siebie
    head_collides_body()

    # Sprawdzamy kolizję piłki z ciałem węża
    check_ball()

    # Sprawdzanie, czy głowa węża trafiła w jakiś element na planszy
    for el in elements[:]:
        if head.colliderect(el):  # Jeżeli głowa węża jest w kolizji z jakimś elementem na planszy
            # W zależności od typu tego elementu, postępujemy inaczej
            if el.element_type == "carrot":
                # Powiększamy węża
                add_body()
                sounds.pickup.play()
                pick_random_pos(el)
                # Zwiększamy licznik punktów
                head.points += 1
                if head.speed > 5:
                    head.speed -= 0.5
            elif el.element_type == "bonus1":
                # Jeżeli wąż ma coś więcej niż tylko głowę
                if len(snake) > 1:
                    snake.pop()

                head.speed -= 1

                elements.remove(el)
            elif el.element_type == "wall":  # jeżeli udeżyliśmy w ścianę
                head.dead = True  # koniec gry
                sounds.lose.play()


def head_collides_body():
    for i in range(1, len(snake)):
        body = snake[i]
        if head.colliderect(body):
            head.dead = True
            sounds.lose.play()


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
        add_body()  # Tymczasowe


# Dodajemy nowy element ciała węża
def add_body():
    body = Actor("snake_body.png")
    # Kopiujemy współrzędne ostatniego elementu węża
    body.x = snake[-1].x
    body.y = snake[-1].y
    body.wait = True  # Oznaczamy, że element czeka 1 klatkę animacji
    snake.append(body)  # Dodajemy nowy element ciała do węża


initialize()

music.play("flow")
music.set_volume(0.1)

pgzrun.go()
