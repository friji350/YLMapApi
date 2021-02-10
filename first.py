import os
import sys
import math
import pygame
import requests

#стандартные значениеы
lon_ = 37.530887 #долгота
lat_ = 55.703118 #широта
zoom_ = 4 #масштаб
map_type = 'map' #надо менять это значение на другие ("sat" например) для решения 4 пункта

#загружаю карту
def load(lon, lat, zoom):
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z={zoom}&l={map_type}"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    

    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    
    return map_file

#обработка нажатия кнопок
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
    elif event.key == pygame.K_PAGEUP and zoom_ < 19: # увеличить масштаб
        zoom_ += 1
    elif event.key == pygame.K_PAGEDOWN and zoom_ > 2: # уменьшить масштаб
        zoom_ -= 1


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    #начальная загрузка карты
    map_image = load(lon_, lat_, zoom_)
    screen.blit(pygame.image.load(map_image), (0, 0))
    pygame.display.flip()

    while True:
        #жду нажатия любой кнопки
        event = pygame.event.wait()
        if event.type == pygame.KEYUP:
            #обнавляю значение
            update(event)
            #загржаю нову карту
            map_image = load(lon_, lat_, zoom_)
            screen.blit(pygame.image.load(map_image), (0, 0))
            pygame.display.flip()
        
        
    pygame.quit()

    os.remove(map_file)

while True:
    main()