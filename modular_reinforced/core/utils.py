def id_generator(agent_id_generator):
    def wrapper_function():
        while 1:
            idx_dict, type = agent_id_generator(IDgenerator)
            idx_dict[type] += 1
            yield type + '_' + str(idx_dict[type])
    return wrapper_function


class IDgenerator(object):
    idx_dict = {
        'unit': 0, 'site': 0, 'factory': 0, 'inventory': 0
    }

    @id_generator
    def unit_id_generator(cls):
        return cls.idx_dict, 'unit'

    @id_generator
    def site_id_generator(cls):
        return cls.idx_dict, 'site'


def unit_id_generator():
    idx = 0
    while 1:
        idx += 1
        yield 'unit_' + str(idx)

def site_id_generator():
    idx = 0
    while 1:
        idx += 1
        yield 'site_' + str(idx)