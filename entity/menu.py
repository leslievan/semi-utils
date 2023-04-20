class MenuComponent:
    """
    抽象菜单组件，提供基础的接口
    """

    def add(self, component):
        """
        添加子项
        :param component:
        :return:
        """
        raise NotImplementedError

    def remove(self, component):
        """
        移除子项
        :param component:
        :return:
        """
        raise NotImplementedError

    def display(self):
        """
        打印菜单
        :return:
        """
        raise NotImplementedError

    def display_item(self):
        """
        打印菜单条目
        :return:
        """
        raise NotImplementedError

    def set_procedure(self, procedure: callable):
        """
        设置菜单对应的操作
        :param procedure:
        :return:
        """
        raise NotImplementedError

    def run(self):
        """
        执行菜单对应的操作
        :return:
        """
        raise NotImplementedError


class Menu(MenuComponent):
    """
    主菜单
    """

    def __init__(self, name):
        self.name = name
        self.components = []

    def add(self, component):
        self.components.append(component)

    def remove(self, component):
        self.components.remove(component)

    def display(self):
        """
        打印二级菜单条目
        :return:
        """
        print(self.name)
        print('-' * 10)
        for idx, component in enumerate(self.components):
            print('【{}】: {}'.format(idx + 1, component.get_active_item()))


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

    def set_value_getter(self, config, getter):
        """
        设置获取子菜单当前值的方法
        :param config:
        :param getter:
        :return:
        """
        self.source = config.get()
        self.getter = getter

    def get_value(self):
        """
        从配置文件中获取子菜单当前值
        :return:
        """
        return self.getter(self.source)

    def set_compare_method(self, method: callable):
        """
        设置比较方法，用子菜单当前值和菜单项对比，判断是否为当前选中项
        :param method:
        :return:
        """
        self.compare_method = method

    def check_active(self):
        """
        检查并更新当前选中项
        :return:
        """
        for idx, component in enumerate(self.components):
            if self.compare_method(self.get_value(), component.get_value()):
                self.is_active = idx

    def get_active_item(self):
        """
        获取子菜单条目值，比如：“左上角: 相机型号”
        :return:
        """
        self.check_active()
        if self.is_active is not None:
            return ': '.join([self.name, self.components[self.is_active].get_active_item()])
        else:
            return ': '.join([self.name, ])

    def display(self):
        """
        打印完整的子菜单选项
        :return:
        """
        print(self.name)
        print('-' * 10)
        for idx, component in enumerate(self.components):
            print('【{}】: {}'.format(idx + 1, ': '.join([self.name, component.get_active_item()])))


class MenuItem(MenuComponent):
    def __init__(self, name):
        self.name = name
        self.procedure = None
        self.value = None

    def get_active_item(self):
        return self.name

    def add(self, component):
        pass

    def get_value(self):
        """
        获取菜单项值，用于比较当前选中项，比如：“LensModel”，提供给配置文件读取
        :return:
        """
        return self.value

    def remove(self, component):
        pass

    def display(self):
        print(self.name)

    def set_procedure(self, procedure: callable):
        """
        设置菜单项的处理方法，比如：更新左上角为相机型号
        :param procedure: 一个无参数的 callable 对象，用于回调
        :return: 
        """
        self.procedure = procedure

    def run(self):
        """
        执行菜单项的处理方法
        :return:
        """
        self.procedure()
