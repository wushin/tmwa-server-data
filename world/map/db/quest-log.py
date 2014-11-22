#!/usr/bin/env python

import sys

assert len(sys.argv) == 2

all_vars = {}

def register_you(name):
    all_vars[name] = [None] * 32

def register_me(var):
    try:
        common = all_vars[var.name]
    except KeyError:
        common = all_vars[var.name] = [None] * 32
    assert var.shift >= 0 and var.width > 0
    for i in range(var.shift, var.shift + var.width):
        assert common[i] is None
        common[i] = var

# quest modes
COMPLETE = 'COMPLETE'
ACTIVE = 'ACTIVE'
REPEAT = 'REPEAT'
STATUS = 'STATUS'

class Var(object):
    __slots__ = ('name', 'shift', 'width', 'quest', 'values')

    def __init__(self, name, shift, width, quest):
        self.name = name
        self.shift = shift
        self.width = width
        self.quest = quest
        self.values = [None] * (1 << width)

        register_me(self)

    def __call__(self, value, desc, mode=ACTIVE, pos=[]):
        assert self.values[value] is None
        self.values[value] = ('%s: %s' % (mode, desc), list(pos))
        return self

    def dump(self, stream):
        stream.write('    set @tmp, (%s >> %d) & ((1 << %d) - 1);\n' % (self.name, self.shift, self.width % 32))
        stream.write('    if (@tmp)\n')
        stream.write('        mes "%s: %s[%d:%d] =" + @tmp;\n' % (self.quest, self.name, self.shift, self.shift + self.width))
        for i, v in enumerate(self.values):
            if v is None:
                stream.write('    // @tmp == %d unused\n' % i)
                continue
            desc, pos = v
            stream.write('    if (@tmp == %d)\n' % i)
            # would be complicated until 'if' is made to take a block
            for m, x, y in pos:
                stream.write('        // %s.gat @ (%d, %d)\n' % (m, x, y))
            assert '"' not in desc and '\\' not in desc
            stream.write('        mes "%s";\n' % desc)
        stream.write('\n')

def finish_it():
    with open(sys.argv[1], 'w') as stream:
        stream.write('// generated file, edit %s instead\n' % __file__)
        stream.write('function|script|QuestLog|,\n')
        stream.write('{\n')
        stream.write('    callfunc "ClearVariables";\n')
        stream.write('\n\n')
        for name, v in sorted(all_vars.items()):
            prev = None
            xbegin = 0
            stream.write('    if (%s)\n' % name)
            stream.write('        mes "%s = " + %s;\n' % (name, name))
            for p in v:
                if p is prev:
                    continue
                prev = p
                if p is None:
                    continue
                if xbegin != p.shift:
                    stream.write('    set @tmp, (%s >> %d) & ((1 << %d) - 1);\n' % (name, xbegin, p.shift % 32))
                    stream.write('    if (@tmp)\n')
                    stream.write('        mes "unclaimed: %s[%d:%d] = " + @tmp;\n' % (name, xbegin, p.shift))
                    stream.write('\n')
                p.dump(stream)
                xbegin = p.shift + p.width
            if xbegin != 32:
                stream.write('    set @tmp, (%s >> %d) & ((1 << %d) - 1);\n' % (name, xbegin, 32 % 32))
                stream.write('    if (@tmp)\n')
                stream.write('        mes "unclaimed: %s[%d:%d] = " + @tmp;\n' % (name, xbegin, 32))
            stream.write('\n\n')
        stream.write('    return;\n')
        stream.write('}\n')

# last-call list of variables
# these should be removed after either:
# 1. they are determined to be special-purpose instead of quest vars
# 2. they are claimed in the actual list
for v in [
    'Annual_Quest',
    'DailyQuestBonus',
    'DailyQuestPoints',
    'DailyQuestTime',
    'FLAGS',
    'HEATHIN_QUEST',
    'Illia_Uniques_Count',
    'Katze',
    'MAGIC_EXPERIENCE',
    'MAGIC_FLAGS',
    'MPQUEST',
    'Menhir_Activated',
    'Mirak_Bantime',
    'Mirak_Questtime',
    'Mobpt',
    'OrumQuest',
    'OrumQuestBarrier',
    'OrumQuestTorch',
    'QUEST_Airlia',
    'QUEST_Barbarians',
    'QUEST_BlueSage',
    'QUEST_Forestbow_state',
    'QUEST_Graveyard_Caretaker',
    'QUEST_Graveyard_Inn',
    'QUEST_Hurnscald',
    'QUEST_MAGIC',
    'QUEST_MAGIC2',
    'QUEST_MIRIAM',
    'QUEST_MIRIAM_cheat',
    'QUEST_MIRIAM_run',
    'QUEST_MIRIAM_start',
    'QUEST_Mirak',
    'QUEST_Nivalis_state',
    'QUEST_NorthTulimshar',
    'QUEST_Scythe_state',
    'QUEST_SouthTulimshar',
    'QUEST_WG_state',
    'QUEST_clothdyer_angus',
    'QUEST_clothdyer_knowsdye',
    'QUEST_clothdyer_state',
    'QUEST_demon_mines',
    'Quest_Halloween',
    'Rossy_Quest',
    'TMW_Quest',
    'TravelFound',
    'XMASTIME',
    'XMASYEAR',
    'cavefights',
    'gotcherry',
    'tvis',
    'wolvern_count',
]:
    register_you(v)

junk = [

Var('STARTAREA', 0, 4, "Tutorial Quest")
(1, "Walk over to the carpet", pos=[('042-2', 33, 27)])
(2, "Retrieve items from the Chest", pos=[('042-2', 27, 23)])
(3, "Open inventory and equip clothes (###keyWindowEquipment;)")
(4, "Find Tanisha", pos=[('042-2', 37, 90)])
(5, "Help Tanisha kill maggots", pos=[('042-2', 37, 90)])
(6, "Help Tanisha kill maggots", pos=[('042-2', 37, 90)])
(7, "Goto Tulimshar", pos=[('042-1', 117, 85)])
(8, "Goto Tulimshar", pos=[('042-1', 117, 85)], mode=COMPLETE)
,

Var('STARTAREA', 0, 4, "Attitude Adjustment")
(9, "Hasan is threating someone.", pos=[('042-1', 117, 85)])
(10, "Kaan said to ask around about his weakness.", pos=[('042-2', 28, 26), ('042-2', 37, 90)])
(11, "Tell Kaan Hasan is afraid of scorpions", pos=[('042-1', 103, 92)])
(12, "Kaan is waiting for the signal to help you get past Hasan", pos=[('042-1', 117, 85)])
(13, "You killed the scorpion and Saved Hasan. Talk to Hasan.")
(14, "You sure taught Hasan a lesson.", mode=COMPLETE)
,

Var('STARTAREA', 1, 4, "Pest Control")
(1, "Talk to Valon", pos=[('042-1', 33, 27)])
(2, "Kill 10 Maggots")
(3, "Kill 5 House Maggots")
(4, "Kill 3 Tame Scorpions")
(5, "Kill 1 Scorpion")
(6, "Complete", mode=COMPLETE)
,

Var('STARTAREA', 3, 4, "MIT: Intro")
(1, "Talk to Morgan", pos=[('042-2', 105, 57)])
(2, "Learn Magic (5+ Int Req.)")
(3, "Cast #Confringo")
(4, "Complete", mode=COMPLETE)
,

Var('STARTAREA', 4, 4, "Barrels O' Fun!")
(1, "Talk to Zegas", pos=[('042-1', 97, 75)])
(2, "Search Barrels")
(3, "Found Bug Bomb. Talk to Zegas")
(4, "Complete", mode=COMPLETE)
,

]
finish_it()
