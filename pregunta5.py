"""
Python 3 Object-Oriented Programming
Chapter 11. Common Design Patterns
"""

#Importamos todas las librerias y archivos externos a utiliar
from __future__ import annotations
import random
import json
import time
from dice import Dice
from typing import List, Protocol
#Patron utilizado: Observer

#Utilizamos el protocol para crear un observer el cual reaccionara a los cambios.
class Observer(Protocol):
    def __call__(self) -> None:
        ...

#Definimos que utilizara el observer para reaccionar en cada cambio
class Observable:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def _notify_observers(self) -> None:
        for observer in self._observers:
            observer()

#Creamos un objeto tipo lista con enteros
Hand = List[int]

#Utilizamos el observer para notificarle a los diferentes "observadores" los cambios registrados en ellos y va notificando a el propio observer.
class ZonkHandHistory(Observable):
    def __init__(self, player: str, dice_set: Dice) -> None:
        super().__init__()
        self.player = player
        self.dice_set = dice_set
        self.rolls: list[Hand]

    def start(self) -> Hand:
        self.dice_set.roll()
        self.rolls = [self.dice_set.dice]
        self._notify_observers()  # Aqui notifica a el observer
        return self.dice_set.dice

    def roll(self) -> Hand:
        self.dice_set.roll()
        self.rolls.append(self.dice_set.dice)
        self._notify_observers()  # Aqui notifica a el observer
        return self.dice_set.dice

#Esta vez notificamos a el observer y lo "llamamos" para hacer los cambios en cada atributo dentro de el
class SaveZonkHand(Observer):
    def __init__(self, hand: ZonkHandHistory) -> None:
        self.hand = hand
        self.count = 0

    def __call__(self) -> None:
        self.count += 1
        message = {
            "player": self.hand.player,
            "sequence": self.count,
            "hands": json.dumps(self.hand.rolls),
            "time": time.time(),
        }
        print(f"SaveZonkHand {message}")

#Se vuelve a utilizar el observer para registrar cada cambio realizado en las funcionalidades y determinar que sucede en el Zonk
class ThreePairZonkHand:
    """Observer of ZonkHandHistory"""

    def __init__(self, hand: ZonkHandHistory) -> None:
        self.hand = hand
        self.zonked = False

    def __call__(self) -> None:
        last_roll = self.hand.rolls[-1]
        distinct_values = set(last_roll)
        self.zonked = len(distinct_values) == 3 and all(
            last_roll.count(v) == 2 for v in distinct_values
        )
        if self.zonked:
            print("3 Pair Zonk!")

#Testeo 1 del history
test_hand_history = """
>>> from unittest.mock import Mock, call
>>> mock_observer = Mock()
>>> import random
>>> random.seed(42)
>>> d = Dice.from_text("6d6")
>>> player = ZonkHandHistory("Bo", d)
>>> player.attach(mock_observer)
>>> player.start()
[1, 1, 2, 3, 6, 6]
>>> player.roll()
[1, 2, 2, 6, 6, 6]
>>> player.rolls
[[1, 1, 2, 3, 6, 6], [1, 2, 2, 6, 6, 6]]
>>> mock_observer.mock_calls
[call(), call()]
"""
#Testeo 1 del observer
test_zonk_observer = """
>>> import random
>>> random.seed(42)
>>> d = Dice.from_text("6d6")
>>> player = ZonkHandHistory("Bo", d)
>>> save_history = SaveZonkHand(player)
>>> player.attach(save_history)
>>> r1 = player.start()
SaveZonkHand {'player': 'Bo', 'sequence': 1, 'hands': '[[1, 1, 2, 3, 6, 6]]', 'time': ...}
>>> r1
[1, 1, 2, 3, 6, 6]
>>> r2 = player.roll()
SaveZonkHand {'player': 'Bo', 'sequence': 2, 'hands': '[[1, 1, 2, 3, 6, 6], [1, 2, 2, 6, 6, 6]]', 'time': ...}
>>> r2
[1, 2, 2, 6, 6, 6]
>>> player.rolls
[[1, 1, 2, 3, 6, 6], [1, 2, 2, 6, 6, 6]]
"""
#Testeo 2 del observer
test_zonk_observer_2 = """
>>> import random
>>> random.seed(21)
>>> d = Dice.from_text("6d6")
>>> player = ZonkHandHistory("David", d)
>>> save_history = SaveZonkHand(player)
>>> player.attach(save_history)
>>> find_3_pair = ThreePairZonkHand(player)
>>> player.attach(find_3_pair)
>>> r1 = player.start()
SaveZonkHand {'player': 'David', 'sequence': 1, 'hands': '[[2, 3, 4, 4, 6, 6]]', 'time': ...}
>>> r1
[2, 3, 4, 4, 6, 6]
>>> r2 = player.roll()
SaveZonkHand {'player': 'David', 'sequence': 2, 'hands': '[[2, 3, 4, 4, 6, 6], [2, 2, 4, 4, 5, 5]]', 'time': ...}
3 Pair Zonk!
>>> r2
[2, 2, 4, 4, 5, 5]
>>> player.rolls
[[2, 3, 4, 4, 6, 6], [2, 2, 4, 4, 5, 5]]
"""

#Aqui es la parte logica del codigo, lo que hara y sucedera con el jugador y los lanzamientos.
def find_seed() -> None:
    d = Dice.from_text("6d6")
    player = ZonkHandHistory("David", d)

    find_3_pair = ThreePairZonkHand(player)
    player.attach(find_3_pair) #Se utiliza para registrar sus cambios implementados

    for s in range(10_000):
        random.seed(s)
        player.start()
        if find_3_pair.zonked:
            print(f"with {s}, roll {player.rolls} ")
        player.roll()
        if find_3_pair.zonked:
            print(f"with {s}, roll {player.rolls} ")

#Probamos los multipes test anteriormente realizados.
__test__ = {name: case for name, case in globals().items() if name.startswith("test_")}

#Le decimos a el codigo si el archivo ejecutado es el main de todos, puede correr el codigo.
if __name__ == "__main__":
    find_seed()