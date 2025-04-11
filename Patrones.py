"""
Este archivo contiene implementaciones corregidas de los 23 patrones de diseño clásicos (GoF)
organizados en las tres categorías principales: Creacionales, Estructurales y de Comportamiento.
Las correcciones principales son en las anotaciones de tipo para clases anidadas.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import copy
import random
import string
from collections.abc import Iterator, Iterable

# =============================================
# PATRONES CREACIONALES (5)
# =============================================

# 1. Abstract Factory
class AbstractFactoryPattern:
    class AbstractFactory(ABC):
        @abstractmethod
        def create_product_a(self):
            pass
        
        @abstractmethod
        def create_product_b(self):
            pass

    class ConcreteFactory1(AbstractFactory):
        def create_product_a(self):
            return AbstractFactoryPattern.ConcreteProductA1()
        
        def create_product_b(self):
            return AbstractFactoryPattern.ConcreteProductB1()

    class ConcreteFactory2(AbstractFactory):
        def create_product_a(self):
            return AbstractFactoryPattern.ConcreteProductA2()
        
        def create_product_b(self):
            return AbstractFactoryPattern.ConcreteProductB2()

    class AbstractProductA(ABC):
        @abstractmethod
        def useful_function_a(self):
            pass

    class ConcreteProductA1(AbstractProductA):
        def useful_function_a(self):
            return "Product A1"

    class ConcreteProductA2(AbstractProductA):
        def useful_function_a(self):
            return "Product A2"

    class AbstractProductB(ABC):
        @abstractmethod
        def useful_function_b(self):
            pass
        
        @abstractmethod
        def another_useful_function_b(self, collaborator: 'AbstractFactoryPattern.AbstractProductA'):
            pass

    class ConcreteProductB1(AbstractProductB):
        def useful_function_b(self):
            return "Product B1"
        
        def another_useful_function_b(self, collaborator: 'AbstractFactoryPattern.AbstractProductA'):
            return f"B1 collaborating with ({collaborator.useful_function_a()})"

    class ConcreteProductB2(AbstractProductB):
        def useful_function_b(self):
            return "Product B2"
        
        def another_useful_function_b(self, collaborator: 'AbstractFactoryPattern.AbstractProductA'):
            return f"B2 collaborating with ({collaborator.useful_function_a()})"

    @staticmethod
    def demo():
        print("\n=== Abstract Factory Pattern Demo ===")
        def client_code(factory: 'AbstractFactoryPattern.AbstractFactory'):
            product_a = factory.create_product_a()
            product_b = factory.create_product_b()
            
            print(product_b.useful_function_b())
            print(product_b.another_useful_function_b(product_a))

        print("Client: Testing client code with the first factory type:")
        client_code(AbstractFactoryPattern.ConcreteFactory1())

        print("\nClient: Testing client code with the second factory type:")
        client_code(AbstractFactoryPattern.ConcreteFactory2())

# 2. Builder
class BuilderPattern:
    class Product:
        def __init__(self):
            self.parts = []
        
        def add(self, part):
            self.parts.append(part)
        
        def list_parts(self):
            print(f"Product parts: {', '.join(self.parts)}")

    class Builder(ABC):
        @abstractmethod
        def build_part_a(self):
            pass
        
        @abstractmethod
        def build_part_b(self):
            pass
        
        @abstractmethod
        def build_part_c(self):
            pass

    class ConcreteBuilder(Builder):
        def __init__(self):
            self.reset()
        
        def reset(self):
            self._product = BuilderPattern.Product()
        
        def build_part_a(self):
            self._product.add("PartA1")
        
        def build_part_b(self):
            self._product.add("PartB1")
        
        def build_part_c(self):
            self._product.add("PartC1")
        
        def get_product(self):
            product = self._product
            self.reset()
            return product

    class Director:
        def __init__(self):
            self._builder = None
        
        @property
        def builder(self):
            return self._builder
        
        @builder.setter
        def builder(self, builder: 'BuilderPattern.Builder'):
            self._builder = builder
        
        def build_minimal_viable_product(self):
            self.builder.build_part_a()
        
        def build_full_featured_product(self):
            self.builder.build_part_a()
            self.builder.build_part_b()
            self.builder.build_part_c()

    @staticmethod
    def demo():
        print("\n=== Builder Pattern Demo ===")
        director = BuilderPattern.Director()
        builder = BuilderPattern.ConcreteBuilder()
        director.builder = builder

        print("Standard basic product:")
        director.build_minimal_viable_product()
        builder.get_product().list_parts()

        print("\nStandard full featured product:")
        director.build_full_featured_product()
        builder.get_product().list_parts()

        print("\nCustom product:")
        builder.build_part_a()
        builder.build_part_c()
        builder.get_product().list_parts()

# 3. Factory Method
class FactoryMethodPattern:
    class Creator(ABC):
        @abstractmethod
        def factory_method(self):
            pass
        
        def some_operation(self):
            product = self.factory_method()
            result = f"Creator: The same creator's code worked with {product.operation()}"
            return result

    class ConcreteCreator1(Creator):
        def factory_method(self):
            return FactoryMethodPattern.ConcreteProduct1()

    class ConcreteCreator2(Creator):
        def factory_method(self):
            return FactoryMethodPattern.ConcreteProduct2()

    class Product(ABC):
        @abstractmethod
        def operation(self):
            pass

    class ConcreteProduct1(Product):
        def operation(self):
            return "Result of ConcreteProduct1"

    class ConcreteProduct2(Product):
        def operation(self):
            return "Result of ConcreteProduct2"

    @staticmethod
    def demo():
        print("\n=== Factory Method Pattern Demo ===")
        def client_code(creator: 'FactoryMethodPattern.Creator'):
            print(f"Client: I'm not aware of the creator's class, but it still works.\n"
                f"{creator.some_operation()}")

        print("App: Launched with ConcreteCreator1.")
        client_code(FactoryMethodPattern.ConcreteCreator1())

        print("\nApp: Launched with ConcreteCreator2.")
        client_code(FactoryMethodPattern.ConcreteCreator2())

# 4. Prototype
class PrototypePattern:
    class Prototype:
        def __init__(self):
            self._objects = {}
        
        def register_object(self, name, obj):
            self._objects[name] = obj
        
        def unregister_object(self, name):
            del self._objects[name]
        
        def clone(self, name, **attrs):
            obj = copy.deepcopy(self._objects[name])
            obj.__dict__.update(attrs)
            return obj

    class Car:
        def __init__(self):
            self.make = "Tesla"
            self.model = "Model S"
            self.color = "Red"
        
        def __str__(self):
            return f"{self.color} {self.make} {self.model}"

    @staticmethod
    def demo():
        print("\n=== Prototype Pattern Demo ===")
        prototype = PrototypePattern.Prototype()
        car = PrototypePattern.Car()
        prototype.register_object("Tesla", car)

        car_clone = prototype.clone("Tesla", color="Blue")
        print(car_clone)

# 5. Singleton
class SingletonPattern:
    class SingletonMeta(type):
        _instances = {}
        
        def __call__(cls, *args, **kwargs):
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]

    class Singleton(metaclass=SingletonMeta):
        def some_business_logic(self):
            pass

    @staticmethod
    def demo():
        print("\n=== Singleton Pattern Demo ===")
        s1 = SingletonPattern.Singleton()
        s2 = SingletonPattern.Singleton()

        if id(s1) == id(s2):
            print("Singleton works, both variables contain the same instance.")
        else:
            print("Singleton failed, variables contain different instances.")

# =============================================
# PATRONES ESTRUCTURALES (7)
# =============================================

# 6. Adapter
class AdapterPattern:
    class Target:
        def request(self):
            return "Target: The default target's behavior."

    class Adaptee:
        def specific_request(self):
            return ".eetpadA eht fo roivaheb laicepS"

    class Adapter(Target):
        def __init__(self, adaptee: 'AdapterPattern.Adaptee'):
            self.adaptee = adaptee
        
        def request(self):
            return f"Adapter: (TRANSLATED) {self.adaptee.specific_request()[::-1]}"

    @staticmethod
    def demo():
        print("\n=== Adapter Pattern Demo ===")
        def client_code(target: 'AdapterPattern.Target'):
            print(target.request())

        target = AdapterPattern.Target()
        client_code(target)

        adaptee = AdapterPattern.Adaptee()
        print(f"Adaptee: {adaptee.specific_request()}")

        adapter = AdapterPattern.Adapter(adaptee)
        client_code(adapter)

# 7. Bridge
class BridgePattern:
    class Implementation(ABC):
        @abstractmethod
        def operation_implementation(self):
            pass

    class ConcreteImplementationA(Implementation):
        def operation_implementation(self):
            return "ConcreteImplementationA"

    class ConcreteImplementationB(Implementation):
        def operation_implementation(self):
            return "ConcreteImplementationB"

    class Abstraction:
        def __init__(self, implementation: 'BridgePattern.Implementation'):
            self._implementation = implementation
        
        def operation(self):
            return f"Abstraction: Base operation with:\n{self._implementation.operation_implementation()}"

    class ExtendedAbstraction(Abstraction):
        def operation(self):
            return f"ExtendedAbstraction: Extended operation with:\n{self._implementation.operation_implementation()}"

    @staticmethod
    def demo():
        print("\n=== Bridge Pattern Demo ===")
        def client_code(abstraction: 'BridgePattern.Abstraction'):
            print(abstraction.operation())

        implementation = BridgePattern.ConcreteImplementationA()
        abstraction = BridgePattern.Abstraction(implementation)
        client_code(abstraction)

        implementation = BridgePattern.ConcreteImplementationB()
        abstraction = BridgePattern.ExtendedAbstraction(implementation)
        client_code(abstraction)

# 8. Composite
class CompositePattern:
    class Component(ABC):
        @property
        def parent(self) -> Optional['CompositePattern.Component']:
            return self._parent
        
        @parent.setter
        def parent(self, parent: 'CompositePattern.Component'):
            self._parent = parent
        
        def add(self, component: 'CompositePattern.Component'):
            pass
        
        def remove(self, component: 'CompositePattern.Component'):
            pass
        
        def is_composite(self) -> bool:
            return False
        
        @abstractmethod
        def operation(self) -> str:
            pass

    class Leaf(Component):
        def operation(self) -> str:
            return "Leaf"

    class Composite(Component):
        def __init__(self):
            self._children: List['CompositePattern.Component'] = []
        
        def add(self, component: 'CompositePattern.Component'):
            self._children.append(component)
            component.parent = self
        
        def remove(self, component: 'CompositePattern.Component'):
            self._children.remove(component)
            component.parent = None
        
        def is_composite(self) -> bool:
            return True
        
        def operation(self) -> str:
            results = []
            for child in self._children:
                results.append(child.operation())
            return f"Branch({'+'.join(results)})"

    @staticmethod
    def demo():
        print("\n=== Composite Pattern Demo ===")
        def client_code(component: 'CompositePattern.Component'):
            print(f"RESULT: {component.operation()}")

        simple = CompositePattern.Leaf()
        client_code(simple)

        tree = CompositePattern.Composite()
        branch1 = CompositePattern.Composite()
        branch1.add(CompositePattern.Leaf())
        branch1.add(CompositePattern.Leaf())
        branch2 = CompositePattern.Composite()
        branch2.add(CompositePattern.Leaf())
        tree.add(branch1)
        tree.add(branch2)

        client_code(tree)

# 9. Decorator
class DecoratorPattern:
    class Component(ABC):
        @abstractmethod
        def operation(self) -> str:
            pass

    class ConcreteComponent(Component):
        def operation(self) -> str:
            return "ConcreteComponent"

    class Decorator(Component):
        def __init__(self, component: 'DecoratorPattern.Component'):
            self._component = component
        
        @property
        def component(self) -> 'DecoratorPattern.Component':
            return self._component
        
        def operation(self) -> str:
            return self._component.operation()

    class ConcreteDecoratorA(Decorator):
        def operation(self) -> str:
            return f"ConcreteDecoratorA({self.component.operation()})"

    class ConcreteDecoratorB(Decorator):
        def operation(self) -> str:
            return f"ConcreteDecoratorB({self.component.operation()})"

    @staticmethod
    def demo():
        print("\n=== Decorator Pattern Demo ===")
        simple = DecoratorPattern.ConcreteComponent()
        decorator1 = DecoratorPattern.ConcreteDecoratorA(simple)
        decorator2 = DecoratorPattern.ConcreteDecoratorB(decorator1)

        print(decorator2.operation())

# 10. Facade
class FacadePattern:
    class Subsystem1:
        def operation1(self) -> str:
            return "Subsystem1: Ready!"
        
        def operation_n(self) -> str:
            return "Subsystem1: Go!"

    class Subsystem2:
        def operation1(self) -> str:
            return "Subsystem2: Get ready!"
        
        def operation_z(self) -> str:
            return "Subsystem2: Fire!"

    class Facade:
        def __init__(self, subsystem1: Optional['FacadePattern.Subsystem1'] = None, 
                    subsystem2: Optional['FacadePattern.Subsystem2'] = None):
            self._subsystem1 = subsystem1 or FacadePattern.Subsystem1()
            self._subsystem2 = subsystem2 or FacadePattern.Subsystem2()
        
        def operation(self) -> str:
            results = []
            results.append(self._subsystem1.operation1())
            results.append(self._subsystem2.operation1())
            results.append(self._subsystem1.operation_n())
            results.append(self._subsystem2.operation_z())
            return "\n".join(results)

    @staticmethod
    def demo():
        print("\n=== Facade Pattern Demo ===")
        subsystem1 = FacadePattern.Subsystem1()
        subsystem2 = FacadePattern.Subsystem2()
        facade = FacadePattern.Facade(subsystem1, subsystem2)
        print(facade.operation())

# 11. Flyweight
class FlyweightPattern:
    class Flyweight:
        def __init__(self, shared_state: List[str]):
            self._shared_state = shared_state
        
        def operation(self, unique_state: List[str]):
            s = ", ".join(map(str, self._shared_state))
            u = ", ".join(map(str, unique_state))
            print(f"Flyweight: Displaying shared ({s}) and unique ({u}) state.")

    class FlyweightFactory:
        _flyweights: Dict[str, 'FlyweightPattern.Flyweight'] = {}
        
        def __init__(self, initial_flyweights: List[List[str]]):
            for state in initial_flyweights:
                self._flyweights[self.get_key(state)] = FlyweightPattern.Flyweight(state)
        
        def get_key(self, state: List[str]) -> str:
            return "_".join(sorted(state))
        
        def get_flyweight(self, shared_state: List[str]) -> 'FlyweightPattern.Flyweight':
            key = self.get_key(shared_state)
            
            if not self._flyweights.get(key):
                print("FlyweightFactory: Can't find a flyweight, creating new one.")
                self._flyweights[key] = FlyweightPattern.Flyweight(shared_state)
            else:
                print("FlyweightFactory: Reusing existing flyweight.")
            
            return self._flyweights[key]
        
        def list_flyweights(self):
            count = len(self._flyweights)
            print(f"FlyweightFactory: I have {count} flyweights:")
            print("\n".join(self._flyweights.keys()))

    @staticmethod
    def demo():
        print("\n=== Flyweight Pattern Demo ===")
        factory = FlyweightPattern.FlyweightFactory([
            ["Chevrolet", "Camaro2018", "pink"],
            ["Mercedes", "C300", "black"],
            ["BMW", "M5", "red"]
        ])

        factory.list_flyweights()

        def add_car_to_police_database(factory: 'FlyweightPattern.FlyweightFactory', 
                                      plates: str, owner: str, brand: str, model: str, color: str):
            flyweight = factory.get_flyweight([brand, model, color])
            flyweight.operation([plates, owner])

        add_car_to_police_database(factory, "CL234IR", "James Doe", "BMW", "M5", "red")
        add_car_to_police_database(factory, "CL678IR", "James Doe", "BMW", "X1", "red")

# 12. Proxy
class ProxyPattern:
    class Subject(ABC):
        @abstractmethod
        def request(self) -> str:
            pass

    class RealSubject(Subject):
        def request(self) -> str:
            return "RealSubject: Handling request."

    class Proxy(Subject):
        def __init__(self, real_subject: 'ProxyPattern.RealSubject'):
            self._real_subject = real_subject
        
        def request(self) -> str:
            if self.check_access():
                result = self._real_subject.request()
                self.log_access()
                return result
            else:
                return "Proxy: Access denied."
        
        def check_access(self) -> bool:
            print("Proxy: Checking access prior to firing a real request.")
            return True
        
        def log_access(self):
            print("Proxy: Logging the time of request.")

    @staticmethod
    def demo():
        print("\n=== Proxy Pattern Demo ===")
        def client_code(subject: 'ProxyPattern.Subject'):
            print(subject.request())

        real_subject = ProxyPattern.RealSubject()
        client_code(real_subject)

        proxy = ProxyPattern.Proxy(real_subject)
        client_code(proxy)

# =============================================
# PATRONES DE COMPORTAMIENTO (11)
# =============================================

# 13. Chain of Responsibility
class ChainOfResponsibilityPattern:
    class Handler(ABC):
        @abstractmethod
        def set_next(self, handler: 'ChainOfResponsibilityPattern.Handler') -> 'ChainOfResponsibilityPattern.Handler':
            pass
        
        @abstractmethod
        def handle(self, request: str) -> Optional[str]:
            pass

    class AbstractHandler(Handler):
        _next_handler: Optional['ChainOfResponsibilityPattern.Handler'] = None
        
        def set_next(self, handler: 'ChainOfResponsibilityPattern.Handler') -> 'ChainOfResponsibilityPattern.Handler':
            self._next_handler = handler
            return handler
        
        def handle(self, request: str) -> Optional[str]:
            if self._next_handler:
                return self._next_handler.handle(request)
            return None

    class MonkeyHandler(AbstractHandler):
        def handle(self, request: str) -> Optional[str]:
            if request == "Banana":
                return f"Monkey: I'll eat the {request}"
            else:
                return super().handle(request)

    class SquirrelHandler(AbstractHandler):
        def handle(self, request: str) -> Optional[str]:
            if request == "Nut":
                return f"Squirrel: I'll eat the {request}"
            else:
                return super().handle(request)

    class DogHandler(AbstractHandler):
        def handle(self, request: str) -> Optional[str]:
            if request == "MeatBall":
                return f"Dog: I'll eat the {request}"
            else:
                return super().handle(request)

    @staticmethod
    def demo():
        print("\n=== Chain of Responsibility Pattern Demo ===")
        def client_code(handler: 'ChainOfResponsibilityPattern.Handler'):
            for food in ["Nut", "Banana", "Cup of coffee"]:
                print(f"\nClient: Who wants a {food}?")
                result = handler.handle(food)
                if result:
                    print(f"  {result}")
                else:
                    print(f"  {food} was left untouched.")

        monkey = ChainOfResponsibilityPattern.MonkeyHandler()
        squirrel = ChainOfResponsibilityPattern.SquirrelHandler()
        dog = ChainOfResponsibilityPattern.DogHandler()

        monkey.set_next(squirrel).set_next(dog)

        client_code(monkey)

# 14. Command
class CommandPattern:
    class Command(ABC):
        @abstractmethod
        def execute(self):
            pass

    class SimpleCommand(Command):
        def __init__(self, payload: str):
            self._payload = payload
        
        def execute(self):
            print(f"SimpleCommand: See, I can do simple things like printing ({self._payload})")

    class ComplexCommand(Command):
        def __init__(self, receiver: 'CommandPattern.Receiver', a: str, b: str):
            self._receiver = receiver
            self._a = a
            self._b = b
        
        def execute(self):
            print("ComplexCommand: Complex stuff should be done by a receiver object")
            self._receiver.do_something(self._a)
            self._receiver.do_something_else(self._b)

    class Receiver:
        def do_something(self, a: str):
            print(f"\nReceiver: Working on ({a}.)")
        
        def do_something_else(self, b: str):
            print(f"Receiver: Also working on ({b}.)")

    class Invoker:
        _on_start: Optional['CommandPattern.Command'] = None
        _on_finish: Optional['CommandPattern.Command'] = None
        
        def set_on_start(self, command: 'CommandPattern.Command'):
            self._on_start = command
        
        def set_on_finish(self, command: 'CommandPattern.Command'):
            self._on_finish = command
        
        def do_something_important(self):
            print("Invoker: Does anybody want something done before I begin?")
            if isinstance(self._on_start, CommandPattern.Command):
                self._on_start.execute()
            
            print("Invoker: ...doing something really important...")
            
            print("Invoker: Does anybody want something done after I finish?")
            if isinstance(self._on_finish, CommandPattern.Command):
                self._on_finish.execute()

    @staticmethod
    def demo():
        print("\n=== Command Pattern Demo ===")
        invoker = CommandPattern.Invoker()
        invoker.set_on_start(CommandPattern.SimpleCommand("Say Hi!"))
        receiver = CommandPattern.Receiver()
        invoker.set_on_finish(CommandPattern.ComplexCommand(
            receiver, "Send email", "Save report"))

        invoker.do_something_important()

# 15. Iterator
class IteratorPattern:
    class AlphabeticalOrderIterator(Iterator):
        _position: int
        _reverse: bool
        
        def __init__(self, collection: List[str], reverse: bool = False):
            self._collection = collection
            self._reverse = reverse
            self._position = -1 if reverse else 0
        
        def __next__(self) -> str:
            try:
                value = self._collection[self._position]
                self._position += -1 if self._reverse else 1
            except IndexError:
                raise StopIteration()
            return value

    class WordsCollection(Iterable):
        def __init__(self, collection: Optional[List[str]] = None):
            self._collection = collection or []
        
        def __iter__(self) -> 'IteratorPattern.AlphabeticalOrderIterator':
            return IteratorPattern.AlphabeticalOrderIterator(self._collection)
        
        def get_reverse_iterator(self) -> 'IteratorPattern.AlphabeticalOrderIterator':
            return IteratorPattern.AlphabeticalOrderIterator(self._collection, True)
        
        def add_item(self, item: str):
            self._collection.append(item)

    @staticmethod
    def demo():
        print("\n=== Iterator Pattern Demo ===")
        collection = IteratorPattern.WordsCollection()
        collection.add_item("First")
        collection.add_item("Second")
        collection.add_item("Third")

        print("Straight traversal:")
        print("\n".join(collection))

        print("\nReverse traversal:")
        print("\n".join(collection.get_reverse_iterator()))

# 16. Mediator
class MediatorPattern:
    class Mediator(ABC):
        @abstractmethod
        def notify(self, sender: object, event: str):
            pass

    class ConcreteMediator(Mediator):
        def __init__(self, component1: 'MediatorPattern.Component1', 
                    component2: 'MediatorPattern.Component2'):
            self._component1 = component1
            self._component1.mediator = self
            self._component2 = component2
            self._component2.mediator = self
        
        def notify(self, sender: object, event: str):
            if event == "A":
                print("Mediator reacts on A and triggers following operations:")
                self._component2.do_c()
            elif event == "D":
                print("Mediator reacts on D and triggers following operations:")
                self._component1.do_b()
                self._component2.do_c()

    class BaseComponent:
        def __init__(self, mediator: Optional['MediatorPattern.Mediator'] = None):
            self._mediator = mediator
        
        @property
        def mediator(self) -> Optional['MediatorPattern.Mediator']:
            return self._mediator
        
        @mediator.setter
        def mediator(self, mediator: 'MediatorPattern.Mediator'):
            self._mediator = mediator

    class Component1(BaseComponent):
        def do_a(self):
            print("Component 1 does A.")
            self.mediator.notify(self, "A")
        
        def do_b(self):
            print("Component 1 does B.")

    class Component2(BaseComponent):
        def do_c(self):
            print("Component 2 does C.")
        
        def do_d(self):
            print("Component 2 does D.")
            self.mediator.notify(self, "D")

    @staticmethod
    def demo():
        print("\n=== Mediator Pattern Demo ===")
        c1 = MediatorPattern.Component1()
        c2 = MediatorPattern.Component2()
        mediator = MediatorPattern.ConcreteMediator(c1, c2)

        print("Client triggers operation A.")
        c1.do_a()

        print("\nClient triggers operation D.")
        c2.do_d()

# 17. Memento
class MementoPattern:
    class Memento:
        def __init__(self, state: str):
            self._state = state
        
        def get_state(self) -> str:
            return self._state

    class Originator:
        _state: str
        
        def __init__(self, state: str):
            self._state = state
            print(f"Originator: My initial state is: {self._state}")
        
        def do_something(self):
            print("Originator: I'm doing something important.")
            self._state = self._generate_random_string(30)
            print(f"Originator: and my state has changed to: {self._state}")
        
        def _generate_random_string(self, length: int = 10) -> str:
            return ''.join(random.choice(string.ascii_letters) for _ in range(length))
        
        def save(self) -> 'MementoPattern.Memento':
            return MementoPattern.Memento(self._state)
        
        def restore(self, memento: 'MementoPattern.Memento'):
            self._state = memento.get_state()
            print(f"Originator: My state has been restored to: {self._state}")

    class Caretaker:
        def __init__(self, originator: 'MementoPattern.Originator'):
            self._mementos: List['MementoPattern.Memento'] = []
            self._originator = originator
        
        def backup(self):
            print("\nCaretaker: Saving Originator's state...")
            self._mementos.append(self._originator.save())
        
        def undo(self):
            if not self._mementos:
                return
            
            memento = self._mementos.pop()
            print(f"Caretaker: Restoring state to: {memento.get_state()}")
            self._originator.restore(memento)
        
        def show_history(self):
            print("Caretaker: Here's the list of mementos:")
            for memento in self._mementos:
                print(memento.get_state())

    @staticmethod
    def demo():
        print("\n=== Memento Pattern Demo ===")
        originator = MementoPattern.Originator("Super-duper-super-puper-super.")
        caretaker = MementoPattern.Caretaker(originator)

        caretaker.backup()
        originator.do_something()

        caretaker.backup()
        originator.do_something()

        caretaker.backup()
        originator.do_something()

        print("\n")
        caretaker.show_history()

        print("\nClient: Now, let's rollback!\n")
        caretaker.undo()

        print("\nClient: Once more!\n")
        caretaker.undo()

# 18. Observer
class ObserverPattern:
    class Subject:
        _observers: List['ObserverPattern.Observer'] = []
        
        def attach(self, observer: 'ObserverPattern.Observer'):
            if observer not in self._observers:
                self._observers.append(observer)
        
        def detach(self, observer: 'ObserverPattern.Observer'):
            try:
                self._observers.remove(observer)
            except ValueError:
                pass
        
        def notify(self):
            for observer in self._observers:
                observer.update(self)

    class ConcreteSubject(Subject):
        _state: int
        
        @property
        def state(self) -> int:
            return self._state
        
        @state.setter
        def state(self, state: int):
            self._state = state
            self.notify()

    class Observer(ABC):
        @abstractmethod
        def update(self, subject: 'ObserverPattern.Subject'):
            pass

    class ConcreteObserverA(Observer):
        def update(self, subject: 'ObserverPattern.Subject'):
            if subject.state < 3:
                print("ConcreteObserverA: Reacted to the event")

    class ConcreteObserverB(Observer):
        def update(self, subject: 'ObserverPattern.Subject'):
            if subject.state == 0 or subject.state >= 2:
                print("ConcreteObserverB: Reacted to the event")

    @staticmethod
    def demo():
        print("\n=== Observer Pattern Demo ===")
        subject = ObserverPattern.ConcreteSubject()

        observer_a = ObserverPattern.ConcreteObserverA()
        subject.attach(observer_a)

        observer_b = ObserverPattern.ConcreteObserverB()
        subject.attach(observer_b)

        subject.state = 1
        subject.state = 2

        subject.detach(observer_a)

        subject.state = 3

# 19. State
class StatePattern:
    class Context:
        _state: Optional['StatePattern.State'] = None
        
        def __init__(self, state: 'StatePattern.State'):
            self.transition_to(state)
        
        def transition_to(self, state: 'StatePattern.State'):
            print(f"Context: Transition to {type(state).__name__}")
            self._state = state
            self._state.context = self
        
        def request1(self):
            if self._state:
                self._state.handle1()
        
        def request2(self):
            if self._state:
                self._state.handle2()

    class State(ABC):
        @property
        def context(self) -> Optional['StatePattern.Context']:
            return self._context
        
        @context.setter
        def context(self, context: 'StatePattern.Context'):
            self._context = context
        
        @abstractmethod
        def handle1(self):
            pass
        
        @abstractmethod
        def handle2(self):
            pass

    class ConcreteStateA(State):
        def handle1(self):
            print("ConcreteStateA handles request1.")
            print("ConcreteStateA wants to change the state of the context.")
            if self.context:
                self.context.transition_to(StatePattern.ConcreteStateB())
        
        def handle2(self):
            print("ConcreteStateA handles request2.")

    class ConcreteStateB(State):
        def handle1(self):
            print("ConcreteStateB handles request1.")
        
        def handle2(self):
            print("ConcreteStateB handles request2.")
            print("ConcreteStateB wants to change the state of the context.")
            if self.context:
                self.context.transition_to(StatePattern.ConcreteStateA())

    @staticmethod
    def demo():
        print("\n=== State Pattern Demo ===")
        context = StatePattern.Context(StatePattern.ConcreteStateA())
        context.request1()
        context.request2()

# 20. Strategy
class StrategyPattern:
    class Context:
        def __init__(self, strategy: 'StrategyPattern.Strategy'):
            self._strategy = strategy
        
        @property
        def strategy(self) -> 'StrategyPattern.Strategy':
            return self._strategy
        
        @strategy.setter
        def strategy(self, strategy: 'StrategyPattern.Strategy'):
            self._strategy = strategy
        
        def do_some_business_logic(self):
            print("Context: Sorting data using the strategy (not sure how it'll do it)")
            result = self._strategy.do_algorithm(["a", "b", "c", "d", "e"])
            print(",".join(result))

    class Strategy(ABC):
        @abstractmethod
        def do_algorithm(self, data: List[str]) -> List[str]:
            pass

    class ConcreteStrategyA(Strategy):
        def do_algorithm(self, data: List[str]) -> List[str]:
            return sorted(data)

    class ConcreteStrategyB(Strategy):
        def do_algorithm(self, data: List[str]) -> List[str]:
            return list(reversed(sorted(data)))

    @staticmethod
    def demo():
        print("\n=== Strategy Pattern Demo ===")
        context = StrategyPattern.Context(StrategyPattern.ConcreteStrategyA())
        print("Client: Strategy is set to normal sorting.")
        context.do_some_business_logic()

        print("\nClient: Strategy is set to reverse sorting.")
        context.strategy = StrategyPattern.ConcreteStrategyB()
        context.do_some_business_logic()

# 21. Template Method
class TemplateMethodPattern:
    class AbstractClass(ABC):
        def template_method(self):
            self.base_operation1()
            self.required_operations1()
            self.base_operation2()
            self.hook1()
            self.required_operations2()
            self.base_operation3()
            self.hook2()
        
        def base_operation1(self):
            print("AbstractClass says: I am doing the bulk of the work")
        
        def base_operation2(self):
            print("AbstractClass says: But I let subclasses override some operations")
        
        def base_operation3(self):
            print("AbstractClass says: But I am doing the bulk of the work anyway")
        
        @abstractmethod
        def required_operations1(self):
            pass
        
        @abstractmethod
        def required_operations2(self):
            pass
        
        def hook1(self):
            pass
        
        def hook2(self):
            pass

    class ConcreteClass1(AbstractClass):
        def required_operations1(self):
            print("ConcreteClass1 says: Implemented Operation1")
        
        def required_operations2(self):
            print("ConcreteClass1 says: Implemented Operation2")

    class ConcreteClass2(AbstractClass):
        def required_operations1(self):
            print("ConcreteClass2 says: Implemented Operation1")
        
        def required_operations2(self):
            print("ConcreteClass2 says: Implemented Operation2")
        
        def hook1(self):
            print("ConcreteClass2 says: Overridden Hook1")

    @staticmethod
    def demo():
        print("\n=== Template Method Pattern Demo ===")
        def client_code(abstract_class: 'TemplateMethodPattern.AbstractClass'):
            abstract_class.template_method()

        print("Same client code can work with different subclasses:")
        client_code(TemplateMethodPattern.ConcreteClass1())

        print("\nSame client code can work with different subclasses:")
        client_code(TemplateMethodPattern.ConcreteClass2())

# 22. Visitor
class VisitorPattern:
    class Component(ABC):
        @abstractmethod
        def accept(self, visitor: 'VisitorPattern.Visitor'):
            pass

    class ConcreteComponentA(Component):
        def accept(self, visitor: 'VisitorPattern.Visitor'):
            visitor.visit_concrete_component_a(self)
        
        def exclusive_method_of_concrete_component_a(self) -> str:
            return "A"

    class ConcreteComponentB(Component):
        def accept(self, visitor: 'VisitorPattern.Visitor'):
            visitor.visit_concrete_component_b(self)
        
        def special_method_of_concrete_component_b(self) -> str:
            return "B"

    class Visitor(ABC):
        @abstractmethod
        def visit_concrete_component_a(self, element: 'VisitorPattern.ConcreteComponentA'):
            pass
        
        @abstractmethod
        def visit_concrete_component_b(self, element: 'VisitorPattern.ConcreteComponentB'):
            pass

    class ConcreteVisitor1(Visitor):
        def visit_concrete_component_a(self, element: 'VisitorPattern.ConcreteComponentA'):
            print(f"{element.exclusive_method_of_concrete_component_a()} + ConcreteVisitor1")
        
        def visit_concrete_component_b(self, element: 'VisitorPattern.ConcreteComponentB'):
            print(f"{element.special_method_of_concrete_component_b()} + ConcreteVisitor1")

    class ConcreteVisitor2(Visitor):
        def visit_concrete_component_a(self, element: 'VisitorPattern.ConcreteComponentA'):
            print(f"{element.exclusive_method_of_concrete_component_a()} + ConcreteVisitor2")
        
        def visit_concrete_component_b(self, element: 'VisitorPattern.ConcreteComponentB'):
            print(f"{element.special_method_of_concrete_component_b()} + ConcreteVisitor2")

    @staticmethod
    def demo():
        print("\n=== Visitor Pattern Demo ===")
        def client_code(components: List['VisitorPattern.Component'], 
                       visitor: 'VisitorPattern.Visitor'):
            for component in components:
                component.accept(visitor)

        components = [
            VisitorPattern.ConcreteComponentA(), 
            VisitorPattern.ConcreteComponentB()
        ]

        print("The client code works with all visitors via the base Visitor interface:")
        visitor1 = VisitorPattern.ConcreteVisitor1()
        client_code(components, visitor1)

        print("\nIt allows the same client code to work with different types of visitors:")
        visitor2 = VisitorPattern.ConcreteVisitor2()
        client_code(components, visitor2)

# 23. Null Object
class NullObjectPattern:
    class AbstractObject:
        def request(self) -> str:
            pass

    class RealObject(AbstractObject):
        def request(self) -> str:
            return "RealObject: Handling request."

    class NullObject(AbstractObject):
        def request(self) -> str:
            return "NullObject: No action taken."

    @staticmethod
    def demo():
        print("\n=== Null Object Pattern Demo ===")
        objects = [
            NullObjectPattern.RealObject(), 
            NullObjectPattern.NullObject(), 
            NullObjectPattern.RealObject()
        ]

        for obj in objects:
            print(obj.request())

# =============================================
# EJECUTAR TODAS LAS DEMOSTRACIONES
# =============================================

def main():
    # Patrones Creacionales
    AbstractFactoryPattern.demo()
    BuilderPattern.demo()
    FactoryMethodPattern.demo()
    PrototypePattern.demo()
    SingletonPattern.demo()
    
    # Patrones Estructurales
    AdapterPattern.demo()
    BridgePattern.demo()
    CompositePattern.demo()
    DecoratorPattern.demo()
    FacadePattern.demo()
    FlyweightPattern.demo()
    ProxyPattern.demo()
    
    # Patrones de Comportamiento
    ChainOfResponsibilityPattern.demo()
    CommandPattern.demo()
    IteratorPattern.demo()
    MediatorPattern.demo()
    MementoPattern.demo()
    ObserverPattern.demo()
    StatePattern.demo()
    StrategyPattern.demo()
    TemplateMethodPattern.demo()
    VisitorPattern.demo()
    NullObjectPattern.demo()

if __name__ == "__main__":
    main()