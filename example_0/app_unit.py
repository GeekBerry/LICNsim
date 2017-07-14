
from common import logging
from base.core import TimeDictDecorator, Packet, NameTable, Timer, Bind, clock, top
from base.unit.app_unit import AppUnitBase
from debug import showCall


class ClientAppUnit(AppUnitBase):
    def __init__(self, keep_time, repeate_time):
        super().__init__()
        self.repeate_time= repeate_time

        self.table= TimeDictDecorator(NameTable(), keep_time)  # {Name:Timer, ...}
        self.table.setTimeEvictCallback(self.timeOut)

    def ask(self, packet):
        # 取消旧定时器
        if packet.name in self.table:
            self.table[packet.name].cancel()
        # 设置新定时器
        timer= Timer( Bind(self.reAsk, packet) )  # 更换新的 packet
        self.table[packet.name]= timer  # 利用 self.table.__setitem__ 激活 TimeDictDecorator 的刷新
        timer.timing(0)

    def reAsk(self, packet):
        assert packet.name in self.table
        packet= packet.fission()
        super().ask(packet)
        self.table[packet.name].timing(self.repeate_time)  # 设置下次定时器
        # logging.info(f'{self} {clock.time()} reAsk {packet}')

    def respond(self, packet):
        pre_names= list( self.table.forebearNames(packet.name) )
        if len(pre_names) > 0:
            for pre_name in pre_names:
                if packet.name == pre_name:  # 对精确匹配的项进行删除
                    per_timer= self.table.pop(pre_name)
                    per_timer.cancel()
                else:  # 对前缀项进行刷新
                    per_timer= self.table[pre_name]
                    per_timer.timing(self.repeate_time)

            super().respond(packet)
            # logging.info(f'{self} {clock.time()} respond {packet}')
        else:
            # logging.info(f'{self} {clock.time()} unPend {packet}')
            pass

    def timeOut(self, name):
        if name in self.table:
            super().respond( Packet(name, Packet.INTEREST, 0) )
            self.table[name].cancel()
            # logging.info(f'{self} {clock.time()} timeOut {name}')


# ----------------------------------------------------------------------------------------------------------------------
ClientAppUnit.UI_ATTRS = {
    'RepeatTime': {
        'type': 'Int',
        'range': (0, 9999_9999),
        'getter': lambda unit: unit.repeate_time,
        'setter': lambda unit, value: setattr(unit, 'repeate_time', value)
    },

    "PendTable":{
        'type':'Table',
        'range':('AskTime', 'Packet'),
        'getter': lambda unit: map( lambda timer:(timer.exe_time, timer.func.args), unit.table.values() )
    }
}

if __name__ == '__main__':
    from common import ip_A, dp_A, dp_A1
    AppUnitBase.ask= Bind(print, 'ask')
    AppUnitBase.respond= Bind(print, 'respond')

    app= ClientAppUnit(10, 5)

    app.ask(ip_A)
    print(app.table)  # TimeDictDecorator({Name('A'): Timer(0: Bind(ClientAppUnit.reAsk (Packet(A, Interest, 1, 0xe4dceb7d),)))})

    for i in range(3):
        clock.step()

    app.respond(dp_A1)
    print(app.table)  # TimeDictDecorator({Name('A'): Timer(8: Bind(ClientAppUnit.reAsk (Packet(A, Interest, 1, 0xe4dceb7d),)))})

    for i in range(10):
        clock.step()

    # -------------------------------------------
    app.ask(ip_A.fission())

    for i in range(3):
        clock.step()

    app.respond(dp_A)
    print(app.table)  # TimeDictDecorator({})
























