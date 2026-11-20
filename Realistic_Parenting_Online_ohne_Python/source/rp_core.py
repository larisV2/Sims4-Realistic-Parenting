# Realistic Parenting - base-game prototype, Python 3.7 compatible
import random

STAT_NAMES = ('trust', 'security', 'independence', 'responsibility', 'rebellion')
LABELS = {'trust': 'Vertrauen', 'security': 'Sicherheit', 'independence': 'Selbststaendigkeit', 'responsibility': 'Verantwortung', 'rebellion': 'Rebellion'}
STYLES = ('warm', 'strict', 'permissive', 'distant', 'protective', 'balanced')
STYLE_LABELS = {'warm':'Liebevoll', 'strict':'Streng', 'permissive':'Nachgiebig', 'distant':'Distanziert', 'protective':'Ueberfuersorglich', 'balanced':'Ausgewogen'}
RULES = ('homework', 'bedtime', 'chores', 'screen', 'curfew')
RULE_LABELS = {'homework':'Hausaufgaben', 'bedtime':'Schlafenszeit', 'chores':'Hausarbeit', 'screen':'Bildschirmzeit', 'curfew':'Ausgehzeit'}
# Each event is (title, situation, choices (label, stat changes))
EVENTS = (
 ('Hausaufgaben verheimlicht', 'Das Kind hat die Hausaufgaben nicht gemacht und gelogen.',
  (('Ruhig sprechen', {'trust':8,'responsibility':4}), ('Hausarrest', {'responsibility':3,'rebellion':7,'trust':-5}), ('Gemeinsam ueben', {'security':6,'responsibility':4,'independence':-2}), ('Ignorieren', {'responsibility':-6,'rebellion':4}))),
 ('Geschwisterstreit', 'Zwei Kinder streiten laut um ein Spielzeug.',
  (('Zuhoeren und vermitteln', {'trust':6,'security':7}), ('Beide bestrafen', {'trust':-5,'rebellion':5}), ('Alleine klaeren lassen', {'independence':6,'security':-3}), ('Ablenken', {'security':2,'responsibility':-2}))),
 ('Schlechte Note', 'Das Kind kommt mit einer schlechten Schulnote nach Hause.',
  (('Ermutigen', {'security':8,'trust':4}), ('Druck machen', {'responsibility':3,'security':-8,'rebellion':4}), ('Lernplan entwickeln', {'responsibility':7,'independence':4}), ('Uebergehen', {'trust':-3,'responsibility':-4}))),
 ('Bildschirmzeit', 'Das Kind nutzt das Tablet laenger als erlaubt.',
  (('Regel erklaeren', {'trust':5,'responsibility':5}), ('Tablet wegnehmen', {'responsibility':4,'rebellion':6}), ('Ausnahme zulassen', {'trust':3,'responsibility':-4}), ('Gemeinsam Alternative suchen', {'security':5,'independence':4}))),
 ('Erster Liebeskummer', 'Das Kind fuehlt sich nach einer Zurueckweisung traurig.',
  (('Gefuehle ernst nehmen', {'security':9,'trust':7}), ('Herunterspielen', {'trust':-8,'security':-6}), ('Rat anbieten', {'trust':4,'independence':2}), ('Privatsphaere geben', {'independence':6,'security':-1}))),
 ('Heimliches Ausgehen', 'Der Teenager war laenger unterwegs als vereinbart.',
  (('Grenzen neu verhandeln', {'trust':6,'responsibility':5}), ('Straf-Hausarrest', {'responsibility':3,'rebellion':9,'trust':-7}), ('Freie Hand lassen', {'independence':6,'responsibility':-5}), ('Sorgen erklaeren', {'security':4,'trust':5}))),
 ('Wutausbruch', 'Das Kind ist frustriert und schreit.',
  (('Begleiten und beruhigen', {'security':9,'trust':4}), ('Anschreien', {'security':-10,'rebellion':7}), ('Zeit zum Beruhigen geben', {'independence':4,'security':2}), ('Nachgeben', {'responsibility':-4,'rebellion':3}))),
 ('Neue Freundschaft', 'Das Kind moechte einen neuen Freund einladen.',
  (('Einladen', {'trust':5,'independence':5}), ('Erst kennenlernen', {'security':4,'responsibility':3}), ('Verbieten', {'trust':-8,'rebellion':7}), ('Kind entscheiden lassen', {'independence':8,'security':-2}))),
 ('Haushaltsaufgabe', 'Das Kind hat seine vereinbarte Aufgabe vergessen.',
  (('Freundlich erinnern', {'trust':4,'responsibility':5}), ('Zusammen erledigen', {'security':5,'responsibility':2}), ('Taschengeld streichen', {'rebellion':6,'trust':-5}), ('Aufgabe selbst erledigen', {'responsibility':-6,'independence':-3}))),
 ('Geheimnis', 'Das Kind bittet dich, ein Geheimnis fuer dich zu behalten.',
  (('Vertraulich anhoeren', {'trust':9,'security':5}), ('Draengen', {'trust':-7,'rebellion':4}), ('Grenzen respektieren', {'trust':5,'independence':5}), ('Nicht zuhoeren', {'trust':-6,'security':-4}))),
 ('Mutprobe', 'Andere Kinder fordern dein Kind zu einer Mutprobe auf.',
  (('Risiken besprechen', {'trust':5,'responsibility':6}), ('Strikt verbieten', {'rebellion':5,'security':-2}), ('Selbst entscheiden lassen', {'independence':7,'responsibility':-2}), ('Zusammen Nein sagen ueben', {'security':6,'independence':5}))),
 ('Entschuldigung', 'Das Kind hat eine Freundin beleidigt und bereut es.',
  (('Entschuldigung ueben', {'responsibility':7,'security':4}), ('Schimpfen', {'trust':-5,'rebellion':5}), ('Freie Entscheidung lassen', {'independence':5,'responsibility':2}), ('Bagatellisieren', {'responsibility':-6})))
)

class FamilyState(object):
    def __init__(self):
        self.children = {}
        self.selected = None
        self.pending = None
        self.history = []
    def ensure_child(self, sim_id, name):
        sim_id = int(sim_id)
        if sim_id not in self.children:
            self.children[sim_id] = {'name':name, 'stats':{'trust':50,'security':50,'independence':50,'responsibility':50,'rebellion':20}, 'style':'balanced', 'rules':dict((r, False) for r in RULES), 'events':0}
        else:
            self.children[sim_id]['name'] = name
        self.selected = sim_id
        return self.children[sim_id]
    def child(self):
        return self.children.get(self.selected)
    def set_style(self, style):
        if style not in STYLES or self.child() is None: return False
        self.child()['style'] = style
        return True
    def set_rule(self, rule, enabled):
        if rule not in RULES or self.child() is None: return False
        self.child()['rules'][rule] = bool(enabled)
        return True
    def new_event(self, index=None):
        if self.child() is None: return None
        if index is None:
            index = random.randrange(len(EVENTS))
        if not 0 <= index < len(EVENTS): return None
        self.pending = (self.selected, index)
        return EVENTS[index]
    def decide(self, option):
        if self.pending is None or not 1 <= option <= 4: return None
        sim_id, idx = self.pending
        if sim_id not in self.children: return None
        child = self.children[sim_id]
        name, delta = EVENTS[idx][2][option-1]
        # Modest contextual influence; the values never leave the 0..100 range.
        effects = dict(delta)
        style = child['style']
        if style == 'warm' and effects.get('trust', 0) > 0: effects['trust'] += 2
        if style == 'strict' and effects.get('rebellion', 0) > 0: effects['rebellion'] += 2
        if style == 'protective' and effects.get('independence', 0) > 0: effects['independence'] -= 2
        if style == 'distant' and effects.get('security', 0) > 0: effects['security'] -= 2
        if style == 'permissive' and effects.get('responsibility', 0) > 0: effects['responsibility'] -= 2
        for stat, diff in effects.items():
            child['stats'][stat] = max(0, min(100, child['stats'][stat] + diff))
        child['events'] += 1
        self.history.append((sim_id, idx, option))
        if len(self.history) > 25: self.history.pop(0)
        self.pending = None
        return (child['name'], name, effects)

STATE = FamilyState()
