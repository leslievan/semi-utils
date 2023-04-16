
class MenuComponent:
    def add(self, component):
        raise NotImplementedError

    def remove(self, component):
        raise NotImplementedError

    def display(self):
        raise NotImplementedError

    def item_display(self):
        raise NotImplementedError


class Menu(MenuComponent):
    def __init__(self, name):
        self.name = name
        self.components = []

    def add(self, component):
        self.components.append(component)

    def remove(self, component):
        self.components.remove(component)

    def display(self):
        print(self.name)
        print('-' * 10)
        for idx, component in enumerate(self.components):
            print('【{}】: {}'.format(idx + 1, component.get_item_value()))


class SubMenu(MenuComponent):
    def __init__(self, name):
        self.name = name
        self.components = []
        self.source = None
        self.getter = None
        self.is_active = None
        self.compare_method = None

    def add(self, component):
        self.components.append(component)

    def remove(self, component):
        self.components.remove(component)

    def set_value(self, source, getter):
        self.source = source
        self.getter = getter

    def get_value(self):
        return self.getter(self.source)

    def set_compare_method(self, method):
        self.compare_method = method

    def check_active(self):
        for idx, component in enumerate(self.components):
            if self.compare_method(self.get_value(), component.get_value()):
                self.is_active = idx

    def get_item_value(self):
        self.check_active()
        if self.is_active is not None:
            return ': '.join([self.name, self.components[self.is_active].get_name()])
        else:
            return ': '.join([self.name, ])

    def display(self):
        print(self.name)
        print('-' * 10)
        for idx, component in enumerate(self.components):
            print('【{}】: {}'.format(idx + 1, self.components[idx].get_name()))


class MenuItem(MenuComponent):
    def __init__(self, name):
        self.name = name
        self.process = None
        self.value = None

    def add(self, component):
        pass

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def remove(self, component):
        pass

    def display(self):
        print(self.name)

    def set_process(self, process):
        self.process = process

    def run(self):
        self.process()

