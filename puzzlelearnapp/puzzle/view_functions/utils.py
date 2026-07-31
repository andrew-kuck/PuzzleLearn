

def clean_display_list(display_list):
    for item in display_list:
        if item['type'] == 'folder':
            item['puzzle_list'] = ''
    return display_list