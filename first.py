import os
import sys
import math
import pygame
import requests

# стандартные значениеы
lon_ = 37.530887  # долгота
lat_ = 55.703118  # широта
zoom_ = 4  # масштаб


# загружаю карту
def load(lon, lat, zoom, map_type):
    api_server = "http://static-maps.yandex.ru/1.x/"
    params = {
        "ll": ",".join(str(i) for i in [lon, lat]),
        'z': zoom,
        "l": map_type
    }
    response = requests.get(api_server, params=params)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    
    return map_file


# обработка нажатия кнопок
def update(event):
    global lon_, lat_, zoom_
    if event.key == pygame.K_LEFT and (lon_ - 0.005 * math.pow(2, 15 - zoom_)) > -185:  # налево
        lon_ -= 0.005 * math.pow(2, 15 - zoom_)
    elif event.key == pygame.K_RIGHT and (lon_ + 0.005 * math.pow(2, 15 - zoom_)) < 180:  # направо
        lon_ += 0.005 * math.pow(2, 15 - zoom_)
    elif event.key == pygame.K_UP and (lat_ + 0.005 * math.pow(2, 15 - zoom_)) < 85:  # вверх
        lat_ += 0.005 * math.pow(2, 15 - zoom_)
    elif event.key == pygame.K_DOWN and (lat_ - 0.005 * math.pow(2, 15 - zoom_)) > -85:  # вниз
        lat_ -= 0.005 * math.pow(2, 15 - zoom_)
    elif event.key == pygame.K_PAGEUP and zoom_ < 19:  # увеличить масштаб
        zoom_ += 1
    elif event.key == pygame.K_PAGEDOWN and zoom_ > 2:  # уменьшить масштаб
        zoom_ -= 1


def draw_l_switching(screen, map_type):
    pygame.draw.rect(screen, 'white', (477, 3, 120, 30))
    pygame.draw.rect(screen, 'gray', (477, 3, 120, 30), 3)
    font = pygame.font.Font(None, 25)
    for i in [['map', (483, 8)], ['sat', (527, 8)], ['hyb', (560, 8)]]:
        if map_type == i[0] or (map_type == 'sat,skl' and i[0] == 'hyb'):
            text = font.render(i[0], True, 'blue')
        else:
            text = font.render(i[0], True, 'gray')
        screen.blit(text, i[1])


def main():
    map_type = 'map'
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    # начальная загрузка карты
    map_image = load(lon_, lat_, zoom_, map_type)
    screen.blit(pygame.image.load(map_image), (0, 0))
    pygame.display.flip()
    while True:
        # жду нажатия любой кнопки
        event = pygame.event.wait()
        if event.type == pygame.KEYUP:
            # обнавляю значение
            update(event)
            # загржаю нову карту
            map_image = load(lon_, lat_, zoom_, map_type)
            screen.blit(pygame.image.load(map_image), (0, 0))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if 483 <= event.pos[0] <= 517 and 3 <= event.pos[1] <= 33:
                map_type = 'map'
            if 527 <= event.pos[0] <= 550 and 3 <= event.pos[1] <= 33:
                map_type = 'sat'
            if 560 <= event.pos[0] <= 593 and 3 <= event.pos[1] <= 33:
                map_type = 'sat,skl'
            map_image = load(lon_, lat_, zoom_, map_type)
            screen.blit(pygame.image.load(map_image), (0, 0))

        draw_l_switching(screen, map_type)
        pygame.display.flip()

    pygame.quit()
    os.remove(map_image)


while True:
    main()
