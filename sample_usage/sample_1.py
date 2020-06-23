from modular_reinforced.core.simulator import MesaModel
import modular_reinforced.core.utils as utils
from modular_reinforced.core.site import SiteAgent
from modular_reinforced.core.inventory import InventoryAgent
from modular_reinforced.core.factory import FactoryAgent
from modular_reinforced.core.element import UnitType
import csv
import logging
sample_model = MesaModel(max_site=15, max_step=500)

with open('../sample_data/site_unit_schedule.csv', 'r') as f:
    f_reader = csv.reader(f)
    site_unit_schedule_list = []
    for idx, row_list in enumerate(f_reader):
        unit_schedule_list = []
        if idx != 0:
            for unit_type in row_list:
                unit_schedule_list.append(UnitType.get_type(unit_type))
            site_unit_schedule_list.append(unit_schedule_list)

for site_unit_schedule in site_unit_schedule_list:
    sample_model.add_site_agent(SiteAgent(100, sample_model, activate=True, unit_schedule=site_unit_schedule))



# for i in range(0, 1000):
#     sample_model.step()
while not sample_model.episode_finished:
    if sample_model.time_step % 10 == 5:
        sample_model.factory.register_production(UnitType.A)
    elif sample_model.time_step % 10 == 0:
        sample_model.factory.register_production(UnitType.B)
    sample_model.step()