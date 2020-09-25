

# Task 1
print("\n==== Task 1. =====\n\n")


class Animal:

  def __init__(self, name, weight):
    self.name = name
    self.weight = weight

  def eat(self):
    print(f"{self.name} жрет")

  def check_voice(self):
    print(f"{self.animail_type} saying: {self.voice}")

class Goose(Animal):

  animail_type = "Гусь"
  voice = "Кряяяя"

  def __init__(self, name, weight, egg_growth):
    super().__init__(name, weight)
    self.egg_growth = egg_growth

  def get_eggs(self):
    print(f"Congratulations! u've earned {self.egg_growth} eggs!")


class Cow(Animal):

  animail_type = "Корова"
  voice = "МУууу"
  
  def get_milk(self):
    print(f"Getting mil from {self.name}")


class Sheep(Animal):

  animail_type = "Баран"
  voice = "Привет, я баран"

  def do_haircut(self):
    print(f"U earned some hair from {self.name}")


class Chicken(Animal):
  
  animail_type = "Курица"
  voice = "коко"

  def __init__(self, name, weight, egg_growth):
    super().__init__(name, weight)
    self.egg_growth = egg_growth
  
  def get_eggs(self):
    print(f"Congratulations! u've earned {self.egg_growth} eggs!")


class Goat(Animal):

  animail_type = "Коза"
  voice = "ыыыыы"

  def get_milk(self):
    print(f"Getting mil from {self.name}")


class Duck(Animal):

  animail_type = "Утка"
  voice = "крякря"

  def get_eggs(self):
    print(f"Congratulations! u've earned {self.egg_growth} eggs!")


farm = []
# goose farm
goose_gray = Goose("Серый", 1, 1)
goose_white = Goose("Белый", 2, 5)
# cow farm
masha = Cow("Манька", 3)
#sheep farm
sheep_barash = Sheep("Барашек", 4)
sheep_kudr = Sheep("Кудрявый", 5)
# chicken farm
chicken_koko = Chicken("Ко-Ко", 6, 1)
chicken_ku = Chicken("Кукареку", 7, 0)
# Goat farm
goat_roga = Goat("Рога", 8)
goat_kopita = Goat("Копыта", 9)
# duck farm
duck_co = Duck("Кряква", 10)

farm.extend([goose_gray, goose_white, masha,
             sheep_barash, sheep_kudr,
             chicken_koko, chicken_ku,
             goat_roga, goat_kopita, duck_co])

# Task 1.2
print("\n==== Task 1.2 =====\n\n")
print("Общий вес:")
print(sum([x.weight for x in farm]))
print("тяжелейшее животное:")
strongest_one = getattr(sorted(farm, key=lambda x: x.weight)[-1], "animail_type")
print(strongest_one)


# Task 2
print("\n==== Task 2 =====\n\n")


class Track:

  def __init__(self, name, dur):
    self._name = name
    self._dur = int(dur)

  def show(self):
    print(f"<{self._name} - {self._dur}>")

  def get_dur(self):
    return self._dur


class Album():

  def __init__(self, name, group):
    self._name = name
    self._group = group
    self._tracklist = []

  def get_tracks(self):
    """
    выводит информацию по всем трекам(используется метод show)
    """
    for track in self._tracklist:
      track.show()
    return self._tracklist

  def add_track(self, track):
    """
    добавление нового трека в список треков
    """
    if track in self._tracklist:
      print("allready in album")
      return
    if type(track) is Track:
      self._tracklist.append(track)
    else:
      print("Добавляем только треки")


  def get_duration(self):
    """
    выводит длительность всего альбома
    """
    return sum([x.get_dur() for x in self._tracklist]) if self._tracklist else 0


tracks = [Track("Нас не догонят", 1),
          Track("Все идет по плану", 5),
          Track("Осьминожек", 4)]


my_album = Album("Избранное", "всяко-разно")
for track in tracks:
  my_album.add_track(track)
my_album.get_tracks()

print(my_album.get_duration())
