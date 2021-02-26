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
postal_code = ""  # индекс найденного
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

    # отрисовка текста и поля
    def draw(self, screen):
        screen.blit(self.text_, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)
    print(distance)
    return distance


def GoCoords(name, positioning=True):
    global lon_, lat_, tag_coords, address, postal_code
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={name}&format=json"

    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()
        if json_response["response"]["GeoObjectCollection"]["featureMember"]:
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            
            address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            try:
                postal_code = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code'] + ', '
            except Exception as e:
                postal_code = 'Индекс не найден, '

            toponym_coodrinates = toponym["Point"]["pos"].split()
            if positioning:
                lon_ = float(toponym_coodrinates[0])
                lat_ = float(toponym_coodrinates[1])
                tag_coords = [str(lon_), str(lat_), 'pm2dbl']
            else:
                tag_coords = [name.split(',')[0], name.split(',')[1], 'pm2dbl']
        else:
            address = 'Ничего не найдено'
            tag_coords = None


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
    if mode:
        if postal_code == 'Индекс не найден, ':
            idx = 58
        else:
            idx = 70
    else:
        idx = 75
    if len(address) > idx:
        print_address = address[:idx] + "..."
    else:
        print_address = address
    if mode:
        print_address = postal_code + print_address

    pygame.draw.rect(screen, 'white', (10, 410, 580, 30))
    pygame.draw.rect(screen, 'gray', (10, 410, 580, 30), 3)
    font = pygame.font.Font(None, 20)
    text = font.render(print_address, True, 'blue')
    screen.blit(text, (15, 419))


def search_organization(coords):
    global tag_coords, address, postal_code
    search_params = {
        "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
        "text": ','.join([coords.split(',')[1], coords.split(',')[0]]),
        "lang": "ru_RU",
        "type": "biz"
    }
    response = requests.get("https://search-maps.yandex.ru/v1/", params=search_params)
    if response:
        print(response.url)
        # Преобразуем ответ в json-объект
        json_response = response.json()
        for organization in json_response["features"]:
            point = organization["geometry"]["coordinates"]
            if lonlat_distance([float(i) for i in point],
                               [float(i) for i in coords.split(',')]) <= 50:
                # Адрес организации
                address = organization["properties"]["CompanyMetaData"]["address"]
                try:
                    postal_code = organization["properties"]["metaDataProperty"][
                        "GeocoderMetaData"]["Address"]['postal_code']
                except Exception as e:
                    postal_code = 'Индекс не найден'
                tag_coords = point.split() + ['pm2dbl']
                break
            else:
                address = 'Ничего не найдено'
                postal_code = 'Индекс не найден'
                tag_coords = None
    else:
        address = 'Ничего не найдено'
        postal_code = 'Индекс не найден'
        tag_coords = None


def geo_coords_to_pixels(coords):
    lon = lon_ + (coords[0] - 300) * 0.0000428 * (2 ** (15 - zoom_))
    lat = lat_ + (255 - coords[1]) * 0.0000428 * (2 ** (15 - zoom_))
    return ','.join([str(round(lon, 6)), str(round(lat, 6))])


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
            if 477 <= event.pos[0] <= 522 and 3 <= event.pos[1] <= 33:
                map_type = 'map'
            elif 523 <= event.pos[0] <= 555 and 3 <= event.pos[1] <= 33:
                map_type = 'sat'
            elif 556 <= event.pos[0] <= 597 and 3 <= event.pos[1] <= 33:
                map_type = 'sat,skl'
            elif 10 <= event.pos[0] <= 130 and 50 <= event.pos[1] <= 80:
                tag_coords = None
                address = ''
                postal_code = ''
            elif 10 <= event.pos[0] <= 60 and 90 <= event.pos[1] <= 120:
                mode = not mode
            elif not (10 <= event.pos[0] <= 510 and 410 <= event.pos[1] <= 440) and\
                    not (10 <= event.pos[0] <= 310 and 10 <= event.pos[1] <= 42) and \
                    not (not mode and 10 <= event.pos[0] <= 210 and 350 <= event.pos[1] <= 380):
                if event.button == 1:
                    GoCoords(geo_coords_to_pixels(event.pos), positioning=False)
                elif event.button == 3:
                    search_organization(geo_coords_to_pixels(event.pos))
            map_image = load(lon_, lat_, zoom_, map_type)
            screen.blit(pygame.image.load(map_image), (0, 0))

        input_text.event_h(event)
        input_text.draw(screen)

        draw_l_switching(screen, map_type)
        DrawDelete(screen)

        draw_address_bar(screen)
        DrawPostalSwitching(screen, mode)

        pygame.display.flip()

    pygame.quit()
    os.remove(map_image)


while True:
    main()
