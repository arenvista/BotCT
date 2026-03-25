from . import base,deck,simple
from .base import EVENT_MAP,update_possibilities

for key,value in EVENT_MAP.items():
    for dep_name in value.dependency_names:
        value.dependencies.append(EVENT_MAP[dep_name])
        
    for antidep_name in value.anti_dependency_names:
        value.anti_dependencies.append(EVENT_MAP[antidep_name])
update_possibilities()     
from .deck import Deck
'''
so when we initialize the object of each event class, we initialize it only with the name
of the dependencies and anti-dependencies, beacuse the actual event object may not have been
instantiated; once all the event objects have been instantiated
THEN we populate the dependency and antidependency lists with the actual objects themselves
'''