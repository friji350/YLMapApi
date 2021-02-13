import os
import sys
import math
import pygame
import requests

# стандартные значениеы
lon_ = 37.530887  # долгота
lat_ = 55.703118  # широта
zoom_ = 8  # масштаб
tag_coords = None  # координаты метки
API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'
address = ""  # адрес найденного объекта
postal_code = "" #индекс найденного
mode = True

class InputText:
    def __init__(self, x, y, text=''):
        self.rect = pygame.Rect(x, y, 300, 32)
        self.color = pygame.Color('gray')
        self.text = text
        self.text_ = pygame.font.Font(None, 32).render(text, True, self.color)
        self.active = False

    def event_h(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            if self.active:
                self.color = pygame.Color('blue')
            else:
                self.color = pygame.Color('gray')
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    GoCoords(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.text_ = pygame.font.Font(None, 32).render(self.text, True, self.color)

    #отрисовка текста и поля
    def draw(self, screen):
        screen.blit(self.text_, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


def GoCoords(name):
    global lon_, lat_, tag_coords, address, postal_code
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={name}&format=json"

    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        if json_response["response"]["GeoObjectCollection"]["featureMember"]:
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            try:
                postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']
            except Exception as e:
                pass


            toponym_coodrinates = toponym["Point"]["pos"].split()

            lon_ = float(toponym_coodrinates[0])
            lat_ = float(toponym_coodrinates[1])
            tag_coords = [str(lon_), str(lat_), 'pm2dbl']
            if len(toponym_address) > 50:
                address = toponym_address[:51] + "..."
            else:
                address = toponym_address
        else:
            address = 'Ничего не найдено'


# загружаю карту
def load(lon, lat, zoom, map_type):
    api_server = "http://static-maps.yandex.ru/1.x/"
    params = {
        "ll": ",".join(str(i) for i in [lon, lat]),
        'z': zoom,
        "l": map_type
    }
    if tag_coords:
        params['pt'] = ','.join(tag_coords)
    response = requests.get(api_server, params=params)

    if not response:
        print("Ошибка выполнения запроса:")
        print(response.url)
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


def DrawDelete(screen):
    pygame.draw.rect(screen, 'white', (10, 50, 120, 30))
    pygame.draw.rect(screen, 'gray', (10, 50, 120, 30), 3)
    text = pygame.font.Font(None, 22).render("Удалить метку", True, pygame.Color('blue'))
    screen.blit(text, (15, 60))

def DrawPostalSwitching(screen, mode):
    pygame.draw.rect(screen, 'white', (10, 90, 50, 30))
    pygame.draw.rect(screen, 'gray', (10, 90, 50, 30), 3)
    if mode:
        text = pygame.font.Font(None, 22).render("On", True, pygame.Color('blue'))
    else:
        text = pygame.font.Font(None, 22).render("Off", True, pygame.Color('blue'))
    screen.blit(text, (15, 95))

def draw_address_bar(screen):
    pygame.draw.rect(screen, 'white', (10, 410, 500, 30))
    pygame.draw.rect(screen, 'gray', (10, 410, 500, 30), 3)
    font = pygame.font.Font(None, 25)
    text = font.render(address, True, 'blue')
    screen.blit(text, (15, 417))

def draw_postal_bar(screen):
    pygame.draw.rect(screen, 'white', (10, 350, 200, 30))
    pygame.draw.rect(screen, 'gray', (10, 350, 200, 30), 3)
    font = pygame.font.Font(None, 25)
    text = font.render(postal_code, True, 'blue')
    screen.blit(text, (15, 355))

def main():
    global tag_coords, address, postal_code, mode
    map_type = 'map'
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    # начальная загрузка карты
    map_image = load(lon_, lat_, zoom_, map_type)
    screen.blit(pygame.image.load(map_image), (0, 0))
    pygame.display.flip()
    input_text = InputText(10, 10)
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
            if 10 <= event.pos[0] <= 130 and 50 <= event.pos[1] <= 80:
                tag_coords = None
                address = ''
                postal_code = ''
            if 10 <= event.pos[0] <= 60 and 90 <= event.pos[1] <= 120:
                mode = not mode
            map_image = load(lon_, lat_, zoom_, map_type)
            screen.blit(pygame.image.load(map_image), (0, 0))

        input_text.event_h(event)
        input_text.draw(screen)

        draw_l_switching(screen, map_type)
        DrawDelete(screen)

        draw_address_bar(screen)
        if not mode:
            draw_postal_bar(screen)
        DrawPostalSwitching(screen, mode)

        pygame.display.flip()

    pygame.quit()
    os.remove(map_image)


while True:
    main()
