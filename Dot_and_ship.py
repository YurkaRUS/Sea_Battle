from random import randint

# Создаем родительский класс для отработки ошибок
class BoardException(Exception):
    pass

# Создаем наследуемые классы для отработки ошибок
# Исключение если пользователь уже стрелял в эту клетку
class BoardUsed(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

# Исключение если полльзователь выстрелил за пределы поля
class BoardOut(BoardException):
    def __str__(self):
        return "Вы выстрелели за пределы поля"

# Исключение если пользователь ввел неверное значение размера поля
class BoardWrongSize(BoardException):
    def __str__(self):
        return "Размер поля не соответствует требуемым параметрам"

# Исключение если пользователь ввел неверные символы
class BoardWrongSimbol(BoardException):
    def __str__(self):
        return "Вы ввели неверные символы"

#
class RepiteEnter(BoardException):
    def __str__(self):
        return "Попробуйте еще раз!"

# Исключение используется для правильной расстановки кораблей (пользователь его не видит)
class BoardWrongShip(BoardException):
    pass


# класс с используемыми обозначениями в поле
class Field:
    empty_field = ('o')
    ship_field = ('S')
    destroyed_field = ('X')
    miss_field = ('•')


# класс точек на нашем поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# применяем магический метод и меняем поведение оператора сравнения для сравнения координат точек
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

# в отличии от метода __str__ будет возвращать значение и воссоздавать объект, а не просто информацию об объекте
    def __str__(self):
        return f"({self.x}, {self.y})"


class Ship:
    # size - длина корабля, rotation - ориентация корабля, bow - начало корабля
    def __init__(self, bow, size, rotation):
        self.bow = bow
        self.size = size
        self.rotation = rotation
        self.hp = size

# Создаем метод dots
    @property
    def dots(self):
        # Создаем список в котором будут содержаться точки корабля
        ship_dots = []
        # цикл от 0 до длины корабля -1
        for i in range(self.size):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.rotation == 0:
                cur_x += i

            elif self.rotation == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

# функция для проверки попадания в корабль (проверяется есть ли точки в нашем списке)
    def shooten(self, shot):
        return shot in self.dots


class Board:
    # Size - размер поля, hid - скрываем поле от пользователя или нет
#    def __init__(self, size, hid = False): в данном случае мы могли бы принят size от пользователя
    def __init__(self, size = 6, hid = False):
        self.size = size
        self.hid = hid
# count - счетчик пораженных кораблей
        self.count = 0
# grid - атрибут создающий сетку поля
        self.grid = [[Field.empty_field] * size for _ in range(size)]
# создаем два пустых списка, busy - занятые клетки, ships - корабли
        self.busy = []
        self.ships = []

    def __str__(self):
        #
        vert_ = "    "
        for j in range(self.size):
            vert_ += f"{j + 1} " + "  "
        for i, row in enumerate(self.grid):
            vert_ += f"\n{i+1}   " + "   ".join(row) + "  "

        if self.hid:
            vert_ = vert_.replace(Field.ship_field, Field.empty_field)
        return vert_

# с помощью этого метода проверяем вылет точки за пределы доски
    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

# этим методом смотрим куда можно поставить наш корабль, чтобы не было соприкосновений с другими кораблями
    def circuit(self, ship, verb=False):
        # список в котором отображены все точки вокруг той в которой мы сейчас находимся
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
# проходим вложенным циклом по всем точкам из нашего списка
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
# если точка не выходит за границы и не занята, добавляем в список busy и ставим на ее месте "."
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.grid[cur.x][cur.y] = Field.miss_field
                    self.busy.append(cur)

# добавляем корабли, первым циклом проверяем условие что корабль не выйдет за границы поля, и точка не занята
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShip
# меняем символ в поле на обозначение нашего корабля
        for d in ship.dots:
            self.grid[d.x][d.y] = Field.ship_field
            self.busy.append(d)
# добавляем корабль в список кораблей и обводим по контуру
        self.ships.append(ship)
        self.circuit(ship)

# метод выстрел, проверяем на отлов ошибок
    def shot(self, d):
        if self.out(d):
            raise BoardOut

        if d in self.busy:
            raise BoardUsed

        self.busy.append(d)
# в цикле проходим по кораблям с проверкой принадлежит ли точка кораблю
        for ship in self.ships:
            if ship.shooten(d):
                ship.hp -= 1
                self.grid[d.x][d.y] = Field.destroyed_field
                if ship.hp == 0:
                    self.count += 1
                    self.circuit(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.grid[d.x][d.y] = Field.miss_field
        print("Мимо!")
        return False

# перед началом игры нужно обновлять список занятых точек
    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

# неопределяем метод по ТЗ, этот метод будет у наследуемых классов
    def ask(self):
        raise NotImplemented()

# пытаемся сделать выстрел пока не введем правильные координаты)))
# запрашиваем координаты, если попали, просим повторить ход
    def move(self):
        while True:
            try:
                target =  self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        global k
        # d = Dot(randint(0, Board.size)), randint(0, Board.size)) вот здесь затык
        d = Dot(randint(0, 5), randint(0, 5))

        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(BoardWrongSimbol())
                print(" Введите 2 координаты! ")
                print(RepiteEnter())
                continue

            x, y = cords

            if not(x.isdigit()) or not(y.isdigit()):
                print(BoardWrongSimbol())
                print("Введите числа! ")
                print(RepiteEnter())
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        # список с длинами кораблей
        sizes = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        # устанавливаем счетчик попыток установки кораблей на доске
        attempts = 0
        for s in sizes:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), s, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShip:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print(
            "___________________",
            "  Приветствуем вас ",
            "      в игре       ",
            "    морской бой    ",
            "___________________",
            " формат ввода: x y ",
            " x - номер строки  ",
            " y - номер столбца ", sep="\n"
        )

    def turn(self):
        # счетчик ходов
        num = 0
        while True:
            print("-" * 20)
            print("Поле пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Поле компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.turn()

# хотелось реализовать выбор пользователем размер игрового поля, но при работе с классом AI программа
# либо уходит в ошибку из-за отсутствия??? в классе Board аттрибута size, либо AI делает 1 ход и завершает программу.
# так и не смог найти затык(((

# while True:
#     try:
#         g = Game(int(input("Введите размер стороны квадрата для построения поля, не менее 5 и не более 10: ")))
#         if int(g.size) >= 5 and int(g.size) <= 10:
#             break
#         else:
#             print(BoardWrongSize())
#             print(RepiteEnter())
#     except ValueError:
#         print(BoardWrongSimbol())
#         print(RepiteEnter())
g = Game()
g.start()
