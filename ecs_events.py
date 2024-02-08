from bearlibterminal import terminal as blt
class EventHandler:
    def __init__(self,ck_dict):
        self.ck_dict = ck_dict

    @property
    def event(self):
        if blt.has_input():
            key = blt.read()
            #print(key)
            if key in self.ck_dict:
                #print("what?")
                _event = self.ck_dict[key]
                return _event
        else:
            return None


def action_maker(event, target):
    if isinstance(target, BaseEntity):
        return Action(event, target)
    if isinstance(target, )
