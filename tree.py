"""модуль работы с деревом"""
import concurrent.futures

from PIL import Image

IMAGE_MAX_DEPTH = 8
ERROR_THRESHOLD = 13


class Point:
    """
    класс точки в двумерном пространстве, заданную координатами x и y
    """
    def __init__(self, x, y):
        """
        Конструктор
        :param x: Координата x
        :param y: Координата y
        """
        self.x = x
        self.y = y

    def __eq__(self, other):
        """
        сравнение двух точек
        :param other: точка для сравнения
        :return: результат сравнения
        """
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        """
        вернуть точку как строку
        :return: строковое представление экземпляра класса
        """
        return f"Точка({self.x}, {self.y})"


def weighted_average(hist):
    """
    вернуть среднюю характеристику и отклонение
    :param hist: гистограмма
    :return: (средневзвешенное значение value и стандартное отклонение error)
    """
    total = sum(hist)
    if total == 0:
        return 0, 0
    value = sum(i * x for i, x in enumerate(hist)) / total
    error = sum(x * (i - value) ** 2 for i, x in enumerate(hist)) / total
    error = error ** 0.5
    return value, error


def color_from_histogram(hist):
    """
    вернуть цвет из гистограммы
    :param hist: гистограмма
    :return: (первый элемент - это кортеж с тремя целочисленными значениями от 0 до 255,
             представляющими красный, зеленый и синий каналы соответственно
             Второй элемент - это число с плавающей точкой, представляющее ошибку,
             вычисленную на основе взвешенного среднего значений ошибок для каждого из каналов цвета)
    """
    red, red_error = weighted_average(hist[:256])
    green, green_error = weighted_average(hist[256:512])
    blue, blue_error = weighted_average(hist[512:768])
    error = red_error * 0.2989 + green_error * 0.5870 + blue_error * 0.1140
    return (int(red), int(green), int(blue)), error


class QuadtreeNode:
    """
    представляет узел квадродерева, который содержит секцию изображения и информацию о ней
    """
    def __init__(self, image, border, depth):
        """
        конструктор
        :param image: изображение для работы
        :param border: границы области узла
        :param depth: глубина узла
        """
        self.__border = border  # регион копирования
        self.__depth = depth
        self.__children = None
        self.__is_leaf = False

        # обрезка части изображения по координатам
        image = image.crop(border)
        hist = image.histogram()
        self.__average_color, self.__error = color_from_histogram(hist)

    @property
    def depth(self):
        """
        вернуть глубину картинки
        :return: глубина картинки
        """
        return self.__depth

    @property
    def error(self):
        """
        :return: вернуть ошибку
        """
        return self.__error

    @property
    def average_color(self):
        """
        вернуть средний цвет
        :return: средний цвет
        """
        return self.__average_color

    @property
    def children(self):
        """
        :return: вернуть дочерние узлы
        """
        return self.__children

    @property
    def border(self):
        """
        :return: вернуть границы(точки)
        """
        return self.__border

    @property
    def is_leaf(self):
        """
        :return: вернуть сравнение квадранта с листом
        """
        return self.__is_leaf

    @is_leaf.setter
    def is_leaf(self, value):
        """
        :param value: задать квадрант
        """
        self.__is_leaf = value

    def split_img(self, image):
        """
        разделить картинку на 4 равные части
        :param image: изображение
        :return: None.
        """

        left, top, right, bottom = self.__border
        width, height = right - left, bottom - top

        if width <= 1 or height <= 1:
            return

        mid_x = (left + right) // 2
        mid_y = (top + bottom) // 2

        self.__children = [
            QuadtreeNode(image, (left, top, mid_x, mid_y), self.__depth + 1),
            QuadtreeNode(image, (mid_x, top, right, mid_y), self.__depth + 1),
            QuadtreeNode(image, (left, mid_y, mid_x, bottom), self.__depth + 1),
            QuadtreeNode(image, (mid_x, mid_y, right, bottom), self.__depth + 1)
        ]


class QuadTree:
    """
    представляет четвертичное дерево, используемое для разбиения изображения на множество
    прямоугольников меньшего размера. он использует рекурсивный алгоритм для деления изображения
    на подобласти до достижения максимальной глубины дерева или достижения минимальной ошибки
    """

    def __init__(self, image):
        """
        конструктор
        :param image: изображение
        """
        self.__width, self.__height = image.size
        self.__root = QuadtreeNode(image, image.getbbox(), 0)
        self.__max_depth = 0
        self.__build_tree(image, self.__root)

    @property
    def width(self):
        """
        возвращает ширину
        :return: вернуть ширину
        """
        return self.__width

    @property
    def height(self):
        """
        возвращает высоту
        :return: вернуть высоту
        """
        return self.__height

    def __build_tree(self, image, node):
        """
        параллельный запуск задач с использованием ThreadPoolExecutor
        каждая задача запускается в отдельном потоке, и метод as_completed()
        используется для получения результатов по мере их завершения
        :param image: изображение
        :param node: узел
        :return: None
        """
        if node.depth >= IMAGE_MAX_DEPTH or node.error <= ERROR_THRESHOLD:
            if node.depth > self.__max_depth:
                self.__max_depth = node.depth
            node.is_leaf = True
            return

        node.split_img(image)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for child in node.children:
                futures.append(executor.submit(self.__build_tree, image, child))

            for future in concurrent.futures.as_completed(futures):
                future.result()

        return None

    def get_leaf_nodes(self, depth):
        """
        вернуть список листов, находящихся на нужной глубине
        :param depth: нужная глубина
        :return: список листов
        """
        if depth > self.__max_depth:
            raise ValueError('дана глубина больше, чем высота деревьев')

        def get_leaf_nodes_recursion(node, curr_depth):
            if curr_depth == depth or node.is_leaf:
                return [node]
            leaf_nodes = []
            for child in node.children:
                leaf_nodes.extend(get_leaf_nodes_recursion(child, curr_depth + 1))
            return leaf_nodes

        return get_leaf_nodes_recursion(self.__root, 0)

    def insert(self, point):
        """
        вставка точки в дерево
        :param point: точка
        """
        self.__insert_recursively(point, self.__root, self.__width, self.__height)

    def __insert_recursively(self, point, node, width, height):
        """
        рекурсивная вставка точки в узел дерева
        :param point: точка для удаления
        :param node: текущий узел
        :param width: ширина
        :param height: высота
        """
        if node.is_leaf:
            return

        left, top, right, bottom = node.border
        mid_x, mid_y = (left + right) // 2, (top + bottom) // 2

        if point.x < mid_x:
            if point.y < mid_y:
                self.__insert_recursively(point, node.children[0], mid_x, mid_y)
            else:
                self.__insert_recursively(point, node.children[2], mid_x, height)
        else:
            if point.y < mid_y:
                self.__insert_recursively(point, node.children[1], width, mid_y)
            else:
                self.__insert_recursively(point, node.children[3], width, height)

    def delete(self, point):
        """
        удаление точки из дерева
        :param point: точка
        """
        self.__delete_recursively(point, self.__root, self.__width, self.__height)

    def __delete_recursively(self, point, node, width, height):
        """
        рекурсивное удаление точки из узла дерева
        :param point: точка для удаления
        :param node: текущий узел
        :param width: ширина
        :param height: высота
        """
        if node.is_leaf:
            return

        left, top, right, bottom = node.border
        mid_x, mid_y = (left + right) // 2, (top + bottom) // 2

        if point.x < mid_x:
            if point.y < mid_y:
                self.__delete_recursively(point, node.children[0], mid_x, mid_y)
            else:
                self.__delete_recursively(point, node.children[2], mid_x, height)
        else:
            if point.y < mid_y:
                self.__delete_recursively(point, node.children[1], width, mid_y)
            else:
                self.__delete_recursively(point, node.children[3], width, height)

    def contains(self, region):
        """
        проверка вхождения области в дерево
        :param region: область для проверки
        :return: True, если область содержится в дереве, иначе False
        """
        return self.__contains_recursively(region, self.__root, self.__width, self.__height)

    def __contains_recursively(self, region, node, width, height):
        """
        рекурсивная проверка на нахождение точки в узле
        :param point: точка для удаления
        :param node: текущий узел
        :param width: ширина
        :param height: высота
        """
        if node.is_leaf:
            return False

        left, top, right, bottom = node.border
        mid_x, mid_y = (left + right) // 2, (top + bottom) // 2

        region_left, region_top, region_right, region_bottom = region

        # Проверка на пересечение областей
        if not (region_right < left or region_left > right or region_bottom < top or region_top > bottom):
            return True

        if region_right < mid_x:
            if region_bottom < mid_y:
                return self.__contains_recursively(region, node.children[0], mid_x, mid_y)
            elif region_top >= mid_y:
                return self.__contains_recursively(region, node.children[2], mid_x, height)

        elif region_left >= mid_x:
            if region_bottom < mid_y:
                return self.__contains_recursively(region, node.children[1], width, mid_y)
            elif region_top >= mid_y:
                return self.__contains_recursively(region, node.children[3], width, height)

        return False


if __name__ == "__main__":
    image_path = "1.png"
    image = Image.open(image_path)

    quadtree = QuadTree(image)

    point_to_insert = Point(x=50, y=50)
    quadtree.insert(point_to_insert)

    point_to_delete = Point(x=30, y=30)
    quadtree.delete(point_to_delete)

    region_to_check = (1000, 1000, 6000, 6000)
    is_contained = quadtree.contains(region_to_check)
    print(f"область {region_to_check} принадлежит дереву? {is_contained}")
