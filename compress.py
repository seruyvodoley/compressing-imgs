"""Модуль для сжатия изображений"""

import os
from PIL import Image, ImageDraw
from tree import QuadTree, IMAGE_MAX_DEPTH


class CreateGif:
    """
    класс создания и сохранения гифки
    """

    def __init__(self):
        """
        конструктор
        :param frames: cписок кадров гифик, который хранит изображения для последующего создания анимации
        :param frames_count: количество кадров в гифке
        :param gif_number: номер текущей гифки создания уникальных названий
        :param path: путь к гифке
        """
        self.frames = []
        self.frames_count = 0
        self.gif_number = 1
        self.path = self._make_path()

    def _make_path(self):
        """
        создать и вернуть путь к гифке
        :return: путь к гифке
        """
        directory = "ГифОчки"

        if not os.path.exists(directory):
            os.mkdir(directory)

        path = os.path.join(directory, f"ГифОчка{self.gif_number}.gif")
        while os.path.exists(path):
            self.gif_number += 1
            path = os.path.join(directory, f"ГифОчка{self.gif_number}.gif")
        return path

    def add_cadr(self, image):
        """
        добавить кадр к гифке
        :param image: кадр
        :return:
        """
        try:
            self.frames_count += 1
            self.frames.append(image)
        except AttributeError:
            print("неверный объект для гифки")
        except Exception as error_message:
            print(f"вышла ошибочка: {error_message}")

    def save_gif(self):
        """
        сохранить гифку в папочку
        :return:
        """
        if self.frames_count == 0:
            print("отменяемс, нет кадров")
            return

        try:
            self.frames[0].save(self.path, save_all=True, append_images=self.frames[1:], optimize=True,
                                duration=800, loop=0)
        except Exception as error_message:
            print(f"вышла ошибочка: {error_message}")
            return

        print("гифка сохранена в ГифОчках")

        for frame in self.frames:
            frame.close()

        self.frames.clear()
        self.frames_count = 0
        self.gif_number += 1


def create_image(quadtree, level, borders):
    """
    создать и вернуть изображение на основе заданного квадродерева, уровня и границ
    :param quadtree: квадродерево
    :param level: уровень дерева
    :param borders: границы
    :return: созданное изображение
    """

    # Создает пустое изображение
    image = Image.new('RGB', (quadtree.width, quadtree.height))

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, quadtree.width, quadtree.height), (0, 0, 0))

    # список узлов квародерева
    nodes_in_leaf = quadtree.get_leaf_nodes(level)

    # отрисовывает прямоугольники, соответствующие границам листовых узлов
    # на изображении, используя цвет усредненный из цветов всех пикселей в этом узле
    # если borders равен True, то границы прямоугольников будут нарисованы черным цветом, а иначе без границ
    for node in nodes_in_leaf:
        if borders:
            draw.rectangle(node.border, node.average_color, outline=(0, 0, 0))
        else:
            draw.rectangle(node.border, node.average_color)

    return image


def save_compressed_image(name, result):
    """
    сохранить файл изображния
    :param name: имя файла
    :param result: сжатое изображение
    :return:
    """
    result.save(f"{name}_сжатое.png")
    print("сжатая фотОчка сохранена")


def compress_and_save_gif(quadtree, borders, gif):
    """
    сжать изображение и сохарнить анимацию
    :param quadtree: квадродерево
    :param borders: границы
    :param gif: экземпляр класса CreateGif(гифка)
    :return:
    """
    for value in range(IMAGE_MAX_DEPTH + 1):
        new_img = create_image(quadtree, value, borders)
        gif.add_cadr(new_img)

    gif.save_gif()
    print("гифка замучена")


def start_compression(file, level, borders, create_gif):
    """
    запустить процесс сжатия изображения и вернуть его
    :param file: путь к сжимаемому изображению
    :param level: уровень сжатия
    :param borders: надо ли рисовать границы или нет
    :param create_gif: надо ли делать гифку или нет
    :return:
    """
    try:
        original_img = Image.open(file)
    except OSError:
        print(f"ошибОчка, не открылся файл{file}")
        return

    quadtree = QuadTree(original_img)

    result = create_image(quadtree, level, borders)
    save_compressed_image(os.path.splitext(file)[0], result)
    print("фотОчка замучена")

    if create_gif:
        gif = CreateGif()
        compress_and_save_gif(quadtree, borders, gif)



