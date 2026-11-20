"""Realistic Parenting v0.1 - base-game cheat-console prototype.
No imports from add-on packs and no invasive overrides.
"""
import sims4.commands
import services
from rp_core import STATE, EVENTS, STYLES, STYLE_LABELS, RULES, RULE_LABELS, STAT_NAMES, LABELS


def out(connection, text):
    sims4.commands.CheatOutput(connection)('[Realistic Parenting] ' + str(text))


def current_household():
    try:
        return services.active_household()
    except Exception:
        return None


def household_members():
    house = current_household()
    return list(house.sim_info_gen()) if house else []


def display_name(sim):
    return '{} {}'.format(sim.first_name, sim.last_name)


def selected_or_help(connection):
    child = STATE.child()
    if child is None:
        out(connection, 'Waehle zuerst ein Kind: parenting.children und parenting.select NUMMER')
    return child


@sims4.commands.Command('parenting.help', command_type=sims4.commands.CommandType.Live)
def rp_help(_connection=None):
    for line in (
        'v0.1 - Cheat-Konsole (Strg+Shift+C), kein testingcheats noetig.',
        'parenting.children  -> Haushalt auflisten',
        'parenting.select 2 -> Sim aus Haushaltsliste waehlen',
        'parenting.status   -> Erziehungswerte anzeigen',
        'parenting.event    -> zufaelliges Familienereignis',
        'parenting.event 1  -> gezieltes Ereignis (1 bis 12)',
        'parenting.choose 1 -> Entscheidung (1 bis 4)',
        'parenting.styles  -> Stile anzeigen',
        'parenting.style warm -> Erziehungsstil aendern',
        'parenting.rules -> Regeln ansehen',
        'parenting.rule homework 1 -> Regel aktivieren (0 = aus)',
        'parenting.history -> letzte Entscheidungen',
        'HINWEIS: Status gilt nur fuer diese Spielsitzung; Speichern folgt spaeter.'
    ): out(_connection, line)


@sims4.commands.Command('parenting.children', command_type=sims4.commands.CommandType.Live)
def rp_children(_connection=None):
    members = household_members()
    if not members: return out(_connection, 'Kein aktiver Haushalt gefunden.')
    out(_connection, 'Haushaltsmitglieder (Nummer fuer parenting.select):')
    for idx, member in enumerate(members, 1):
        out(_connection, '{}: {}'.format(idx, display_name(member)))
    out(_connection, 'Bitte nur Kinder/Teenager auswaehlen. Alterspruefung kommt in einer spaeteren Version.')


@sims4.commands.Command('parenting.select', command_type=sims4.commands.CommandType.Live)
def rp_select(index: int = 0, _connection=None):
    members = household_members()
    if index < 1 or index > len(members): return out(_connection, 'Ungueltige Nummer. Zuerst parenting.children eingeben.')
    sim = members[index-1]
    try:
        child = STATE.ensure_child(sim.sim_id, display_name(sim))
    except Exception as exc:
        return out(_connection, 'Auswahl fehlgeschlagen: {}'.format(exc))
    out(_connection, '{} ausgewaehlt. parenting.status zeigt die Werte.'.format(child['name']))


@sims4.commands.Command('parenting.status', command_type=sims4.commands.CommandType.Live)
def rp_status(_connection=None):
    child = selected_or_help(_connection)
    if child is None: return
    out(_connection, '{} | Stil: {} | Ereignisse: {}'.format(child['name'], STYLE_LABELS[child['style']], child['events']))
    for stat in STAT_NAMES:
        out(_connection, '{}: {}/100'.format(LABELS[stat], child['stats'][stat]))
    out(_connection, 'Regeln: {}'.format(', '.join(RULE_LABELS[k] for k in RULES if child['rules'][k]) or 'Keine'))


@sims4.commands.Command('parenting.event', command_type=sims4.commands.CommandType.Live)
def rp_event(index: int = 0, _connection=None):
    if selected_or_help(_connection) is None: return
    event = STATE.new_event(index-1 if index else None)
    if event is None: return out(_connection, 'Ereignisnummer muss 1 bis {} sein.'.format(len(EVENTS)))
    out(_connection, 'EREIGNIS: {} | {}'.format(event[0], event[1]))
    for i, option in enumerate(event[2], 1):
        out(_connection, '{}: {}'.format(i, option[0]))
    out(_connection, 'Waehle: parenting.choose 1 / 2 / 3 / 4')


@sims4.commands.Command('parenting.choose', command_type=sims4.commands.CommandType.Live)
def rp_choose(index: int = 0, _connection=None):
    result = STATE.decide(index)
    if result is None: return out(_connection, 'Keine gueltige Entscheidung. Zuerst parenting.event, dann parenting.choose 1-4.')
    name, action, effects = result
    out(_connection, '{}: {}'.format(name, action))
    for stat in STAT_NAMES:
        if effects.get(stat): out(_connection, '{}: {:+d}'.format(LABELS[stat], effects[stat]))
    out(_connection, 'parenting.status zeigt die aktualisierten Werte.')


@sims4.commands.Command('parenting.styles', command_type=sims4.commands.CommandType.Live)
def rp_styles(_connection=None):
    for style in STYLES: out(_connection, '{} = {}'.format(style, STYLE_LABELS[style]))
    out(_connection, 'Beispiel: parenting.style warm')


@sims4.commands.Command('parenting.style', command_type=sims4.commands.CommandType.Live)
def rp_style(style: str = '', _connection=None):
    style = style.lower()
    if not STATE.set_style(style): return out(_connection, 'Stil ungueltig oder kein Kind gewaehlt. parenting.styles')
    out(_connection, 'Erziehungsstil: {}'.format(STYLE_LABELS[style]))


@sims4.commands.Command('parenting.rules', command_type=sims4.commands.CommandType.Live)
def rp_rules(_connection=None):
    child = selected_or_help(_connection)
    if child is None: return
    for key in RULES:
        out(_connection, '{} ({}): {}'.format(RULE_LABELS[key], key, 'AN' if child['rules'][key] else 'AUS'))
    out(_connection, 'Beispiel: parenting.rule bedtime 1')
    out(_connection, 'Aktuell: dokumentierte Familienregeln, noch keine automatische Durchsetzung.')


@sims4.commands.Command('parenting.rule', command_type=sims4.commands.CommandType.Live)
def rp_rule(rule: str = '', enabled: int = -1, _connection=None):
    rule = rule.lower()
    if enabled not in (0, 1) or not STATE.set_rule(rule, bool(enabled)):
        return out(_connection, 'Syntax: parenting.rule homework 1 (oder 0); parenting.rules')
    out(_connection, '{}: {}'.format(RULE_LABELS[rule], 'AN' if enabled else 'AUS'))


@sims4.commands.Command('parenting.history', command_type=sims4.commands.CommandType.Live)
def rp_history(_connection=None):
    if not STATE.history: return out(_connection, 'Noch keine Entscheidungen in dieser Sitzung.')
    for sim_id, event_id, option in STATE.history[-10:]:
        c = STATE.children.get(sim_id)
        out(_connection, '{} | {} | {}'.format(c['name'] if c else sim_id, EVENTS[event_id][0], EVENTS[event_id][2][option-1][0]))
