import geonamescache

def clean_display_list(display_list):
    for item in display_list:
        if item['type'] == 'folder':
            item['puzzle_list'] = ''
        if item.get('template_dict_function'):
            item['template_dict_function'] = ''
    return display_list


def get_geo_meta():
    try:
        gc = geonamescache.GeonamesCache()
        countries = gc.get_countries()
        countries_list = [
            {'iso': iso, 'name': c.get('name',''), 'continent': c.get('continentcode','')}
            for iso, c in countries.items()
        ]
        us_states = gc.get_us_states()
        us_states_list = [{'code': k, 'name': v.get('name','')} for k, v in us_states.items()]
    except Exception:
        countries_list = []
        us_states_list = []
    return {'geo_meta': {'countries': countries_list, 'us_states': us_states_list}}