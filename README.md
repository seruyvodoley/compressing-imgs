# Сжатие изображения с использованием квадродерева
Дерево должно поддержиет следующие методы:
- вставка
- удаление
- вхождение в диапазон/область (для 2d)/объем (для 3d)

### Сжатие изображений

Реализована консольная утилита

Предусмотрено:
1. Сжатие изображения с помощью квадродеревьев.
2. Сохранение итогового изображения.
3. Сохранение изображения с границами построенного дерева.
4. Указание степени сжатия.
5. Использование потоков для сжатия отдельных областей.
6. Создание гифки пошагового сжатия любой картинки

Запустить можно командой
```bash
python main.py -f img.png -c 5 -s -g
```
где: 
-с - уровень сжатия
-s - отображение границ
-g - создание гифки

