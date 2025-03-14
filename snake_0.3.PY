import pygame
import random
import sys

# Inicializar pygame
pygame.init()

# Definir colores
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_GREEN = (0, 100, 0)
OCEAN_BLUE = (0, 119, 190)
LAVA_RED = (207, 16, 32)

# Definir dimensiones de la ventana
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800

# Crear la ventana
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Snake Game Modificado')

# Cargar imágenes de fondo
fondo_menu = pygame.image.load("snake.png")  # Fondo para menú y configuración
fondo_menu = pygame.transform.scale(fondo_menu, (WINDOW_WIDTH, WINDOW_HEIGHT))

fondos_juego = {
    "pasto": pygame.image.load("pasto.png"),  # Asegúrate de tener una imagen llamada "pasto.png"
    "oceano": pygame.image.load("oceano.png"),  # Asegúrate de tener una imagen llamada "oceano.png"
    "volcan": pygame.image.load("volcan.png")  # Asegúrate de tener una imagen llamada "volcan.png"
}
for key in fondos_juego:
    fondos_juego[key] = pygame.transform.scale(fondos_juego[key], (WINDOW_WIDTH, WINDOW_HEIGHT))

# Reloj para controlar la velocidad del juego
clock = pygame.time.Clock()

# Tamaños del mapa (en celdas)
TAMAÑOS_MAPA = {
    "pequeño": (20, 20),  # 20x20 celdas
    "mediano": (30, 30),  # 30x30 celdas
    "grande": (45, 45)    # 45x45 celdas
}

# Tamaño inicial del mapa
tamaño_mapa_actual = "mediano"
mapa_ancho, mapa_alto = TAMAÑOS_MAPA[tamaño_mapa_actual]

# Tamaño de cada celda (en píxeles)
# Calculamos el tamaño de la celda en función del tamaño del mapa y la ventana
celda_ancho = WINDOW_WIDTH // mapa_ancho
celda_alto = WINDOW_HEIGHT // mapa_alto

# Fuentes para el texto
font_style = pygame.font.SysFont("bahnschrift", 50)
score_font = pygame.font.SysFont("comicsansms", 35)

# Variables globales para las modificaciones
modificaciones = {
    "tipo_comida": "manzana",  # manzana, zanahoria, uva
    "cantidad_comida": 1,  # 1, 3, 5, aleatorio
    "velocidad": "normal",  # normal, conejo, tortuga
    "tamaño_mapa": tamaño_mapa_actual,  # pequeño, mediano, grande
    "color_serpiente": "Verde",  # Verde, Rojo, Azul, Amarillo, Blanco
    "diseño_mapa": "pasto",  # pasto, oceano, volcan
    "modo_juego": "normal",  # normal, bloques_mortales, cambio_direccion, barreras_frutas
}

manzanas_obtenidas = 0
trofeos = 0

def draw_snake(snake_list, color):
    for block in snake_list:
        pygame.draw.rect(window, color, [block[0], block[1], celda_ancho, celda_alto], border_radius=5)

def display_score(score):
    value = score_font.render("Puntuación: " + str(score), True, YELLOW)
    window.blit(value, [10, 10])

def draw_message(msg, color, y_offset=0):
    mesg = font_style.render(msg, True, color)
    window.blit(mesg, [WINDOW_WIDTH / 2 - mesg.get_width() / 2, WINDOW_HEIGHT / 2 - mesg.get_height() / 2 + y_offset])

def spawn_food(food_list):
    x = random.randint(0, mapa_ancho - 1) * celda_ancho
    y = random.randint(0, mapa_alto - 1) * celda_alto
    food_list.append((x, y))

def crear_barreras(food_list):
    barreras = {}  # Cambio a diccionario para asociar barreras con frutas
    for food in food_list:
        barreras[food] = []
        for _ in range(2):  # Crear 2 barreras por fruta
            barreras[food].append((food[0] + random.choice([-celda_ancho, celda_ancho]),
                            food[1] + random.choice([-celda_alto, celda_alto])))
    return barreras

def generar_bloque_mortal(snake_head, x1_change, y1_change):
    while True:
        x = random.randint(0, mapa_ancho - 1) * celda_ancho
        y = random.randint(0, mapa_alto - 1) * celda_alto

        # Verificar que el bloque no esté justo delante de la serpiente
        frente_serpiente_x = snake_head[0] + x1_change
        frente_serpiente_y = snake_head[1] + y1_change

        if (x, y) != (frente_serpiente_x, frente_serpiente_y):
            return (x, y)

def cambiar_tamaño_mapa(nuevo_tamaño):
    global mapa_ancho, mapa_alto, celda_ancho, celda_alto
    mapa_ancho, mapa_alto = TAMAÑOS_MAPA[nuevo_tamaño]
    celda_ancho = WINDOW_WIDTH // mapa_ancho
    celda_alto = WINDOW_HEIGHT // mapa_alto

def game_loop():
    global manzanas_obtenidas
    game_over = False
    game_close = False

    # Posición inicial de la serpiente
    x1 = (mapa_ancho // 2) * celda_ancho
    y1 = (mapa_alto // 2) * celda_alto

    # Cambio en la posición
    x1_change = 0
    y1_change = 0

    # Cuerpo de la serpiente
    snake_list = []
    length_of_snake = 1

    # Comida
    food_list = []
    for _ in range(modificaciones["cantidad_comida"] if modificaciones["cantidad_comida"] != "aleatorio" else random.choice([1, 3, 5])):
        spawn_food(food_list)

    # Barreras en las frutas (si el modo de juego lo requiere)
    barreras = {}
    if modificaciones["modo_juego"] == "barreras_frutas":
        barreras = crear_barreras(food_list)

    # Bloques mortales (si el modo de juego lo requiere)
    bloques = []

    while not game_over:
        while game_close:
            window.blit(fondo_menu, (0, 0))  # Fondo fijo para el menú de game over
            draw_message("¡Perdiste! Presiona C para jugar de nuevo", RED, -50)
            draw_message("Presiona M para volver al menú", WHITE, 50)
            display_score(length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        game_loop()
                        return  # Importante: salir completamente de la función actual
                    if event.key == pygame.K_m:
                        return  # Volver directamente al menú principal

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -celda_ancho
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = celda_ancho
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -celda_alto
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = celda_alto
                    x1_change = 0

        # Si la serpiente choca con los bordes del mapa
        if x1 >= WINDOW_WIDTH or x1 < 0 or y1 >= WINDOW_HEIGHT or y1 < 0:
            game_close = True

        # Mover la serpiente
        x1 += x1_change
        y1 += y1_change
        window.blit(fondos_juego[modificaciones["diseño_mapa"]], (0, 0))  # Fondo dinámico para el juego

        # Dibujar la comida
        for food in food_list:
            if modificaciones["tipo_comida"] == "manzana":
                pygame.draw.rect(window, RED, [food[0], food[1], celda_ancho, celda_alto], border_radius=10)
            elif modificaciones["tipo_comida"] == "zanahoria":
                pygame.draw.rect(window, ORANGE, [food[0], food[1], celda_ancho, celda_alto], border_radius=10)
            elif modificaciones["tipo_comida"] == "uva":
                pygame.draw.rect(window, PURPLE, [food[0], food[1], celda_ancho, celda_alto], border_radius=10)

        # Dibujar barreras en las frutas (si el modo de juego lo requiere)
        if modificaciones["modo_juego"] == "barreras_frutas":
            todas_barreras = []
            for food, barrera_lista in barreras.items():
                todas_barreras.extend(barrera_lista)
            
            for barrera in todas_barreras:
                pygame.draw.rect(window, WHITE, [barrera[0], barrera[1], celda_ancho, celda_alto], border_radius=5)

        # Dibujar bloques mortales (si el modo de juego lo requiere)
        if modificaciones["modo_juego"] == "bloques_mortales":
            for bloque in bloques:
                pygame.draw.rect(window, WHITE, [bloque[0], bloque[1], celda_ancho, celda_alto], border_radius=5)

        # Añadir la cabeza de la serpiente
        snake_head = (x1, y1)
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Si la serpiente choca consigo misma
        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        # Si la serpiente choca con bloques mortales
        if modificaciones["modo_juego"] == "bloques_mortales":
            for bloque in bloques:
                if snake_head == bloque:
                    game_close = True

        # Si la serpiente choca con barreras
        if modificaciones["modo_juego"] == "barreras_frutas":
            todas_barreras = []
            for food, barrera_lista in barreras.items():
                todas_barreras.extend(barrera_lista)
            
            for barrera in todas_barreras:
                if snake_head == barrera:
                    game_close = True

        # Dibujar la serpiente
        snake_color = {
            "Verde": GREEN,
            "Rojo": RED,
            "Azul": BLUE,
            "Amarillo": YELLOW,
            "Blanco": WHITE
        }[modificaciones["color_serpiente"]]
        draw_snake(snake_list, snake_color)

        # Mostrar la puntuación
        display_score(length_of_snake - 1)

        # Actualizar la pantalla
        pygame.display.update()

        # Si la serpiente come la comida
        for food in list(food_list):  # Usar una copia de la lista para poder modificarla
            if x1 == food[0] and y1 == food[1]:
                food_list.remove(food)
                # Eliminar las barreras asociadas a esta fruta
                if modificaciones["modo_juego"] == "barreras_frutas" and food in barreras:
                    del barreras[food]
                
                spawn_food(food_list)
                length_of_snake += 1
                manzanas_obtenidas += 1

                # Cambio de dirección al comer
                if modificaciones["modo_juego"] == "cambio_direccion":
                    x1_change, y1_change = y1_change, x1_change

                # Crear bloques mortales
                if modificaciones["modo_juego"] == "bloques_mortales":
                    nuevo_bloque = generar_bloque_mortal(snake_head, x1_change, y1_change)
                    bloques.append(nuevo_bloque)

                # Crear barreras para la nueva fruta (si el modo de juego lo requiere)
                if modificaciones["modo_juego"] == "barreras_frutas":
                    nuevas_barreras = {}
                    for f in food_list:
                        if f not in barreras:  # Solo crear barreras para frutas nuevas
                            nuevas_barreras[f] = []
                            for _ in range(2):
                                nuevas_barreras[f].append((f[0] + random.choice([-celda_ancho, celda_ancho]),
                                                      f[1] + random.choice([-celda_alto, celda_alto])))
                    # Actualizar el diccionario de barreras
                    barreras.update(nuevas_barreras)

        # Controlar la velocidad del juego
        if modificaciones["velocidad"] == "conejo":
            clock.tick(30)
        elif modificaciones["velocidad"] == "tortuga":
            clock.tick(5)
        else:
            clock.tick(15)

def main():
    global manzanas_obtenidas, tamaño_mapa_actual
    opcion_seleccionada = 0
    in_configuracion = False

    while True:
        if not in_configuracion:
            window.blit(fondo_menu, (0, 0))  # Fondo fijo para el menú
            draw_message("Snake Game Modificado", GREEN, -200)
            draw_message(f"Manzanas: {manzanas_obtenidas}", WHITE, -100)
            draw_message(f"Trofeos: {trofeos}", WHITE, -50)
            draw_message("1 - Jugar", WHITE, 50)
            draw_message("2 - Configuración", WHITE, 100)
            draw_message("3 - Desafíos", WHITE, 150)
            pygame.display.update()
        else:
            window.blit(fondo_menu, (0, 0))  # Fondo fijo para la configuración
            draw_message("Configuración", GREEN, -200)
            opciones = [
                "1 - Tipo de comida: " + modificaciones["tipo_comida"],
                "2 - Cantidad de comida: " + str(modificaciones["cantidad_comida"]),
                "3 - Velocidad: " + modificaciones["velocidad"],
                "4 - Tamaño del mapa: " + modificaciones["tamaño_mapa"],
                "5 - Color de la serpiente: " + modificaciones["color_serpiente"],
                "6 - Diseño del mapa: " + modificaciones["diseño_mapa"],
                "7 - Modo de juego: " + modificaciones["modo_juego"],
                "P - Volver al menú principal"
            ]
            for i, opcion in enumerate(opciones):
                color = YELLOW if i == opcion_seleccionada else WHITE
                draw_message(opcion, color, -150 + i * 50)
            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not in_configuracion:
                    if event.key == pygame.K_1:
                        game_loop()
                    elif event.key == pygame.K_2:
                        in_configuracion = True
                    elif event.key == pygame.K_3:
                        pass  # Lógica para desafíos
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                else:
                    if event.key == pygame.K_UP:
                        opcion_seleccionada = (opcion_seleccionada - 1) % 8
                    elif event.key == pygame.K_DOWN:
                        opcion_seleccionada = (opcion_seleccionada + 1) % 8
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_p:
                        if opcion_seleccionada == 7:  # Opción "P - Volver al menú principal"
                            in_configuracion = False
                        else:
                            # Cambiar las configuraciones
                            if opcion_seleccionada == 0:
                                modificaciones["tipo_comida"] = random.choice(["manzana", "zanahoria", "uva"])
                            elif opcion_seleccionada == 1:
                                modificaciones["cantidad_comida"] = random.choice([1, 3, 5, "aleatorio"])
                            elif opcion_seleccionada == 2:
                                modificaciones["velocidad"] = random.choice(["normal", "conejo", "tortuga"])
                            elif opcion_seleccionada == 3:
                                tamaño_mapa_actual = random.choice(["pequeño", "mediano", "grande"])
                                cambiar_tamaño_mapa(tamaño_mapa_actual)
                                modificaciones["tamaño_mapa"] = tamaño_mapa_actual
                            elif opcion_seleccionada == 4:
                                modificaciones["color_serpiente"] = random.choice(["Verde", "Rojo", "Azul", "Amarillo", "Blanco"])
                            elif opcion_seleccionada == 5:
                                modificaciones["diseño_mapa"] = random.choice(["pasto", "oceano", "volcan"])
                            elif opcion_seleccionada == 6:
                                modificaciones["modo_juego"] = random.choice(["normal", "bloques_mortales", "cambio_direccion", "barreras_frutas"])

if __name__ == "__main__":
    main()