from .utils import get_geo_meta

puzzle_list = [

    {
        'type': 'static_question_collection',
        'name': ''
    },

    {
        'type': 'folder',
        'name': 'basic_math',
        'display_name': 'Basic Math',
        'puzzle_list': [
            {'type': 'file', 'name': 'multiplication_number_bonds', 'display_name': 'Multiplication Number Bonds'},
            {'type': 'file', 'name': 'negative_number_bonds', 'display_name': 'Negative Number Bonds'},
            {'type': 'file', 'name': 'fraction_number_bonds', 'display_name': 'Fraction Number Bonds'},
            {'type': 'file', 'name': 'number_line_placement', 'display_name': 'Number Line Placement'},
            {'type': 'file', 'name': 'number_line_jumps', 'display_name': 'Number Line Jumps'},
            {'type': 'file', 'name': 'order_of_operations_(easy)', 'display_name': 'Order of Operations (easy)'},
            {'type': 'file', 'name': 'order_of_operations_(difficult)', 'display_name': 'Order of Operations (difficult)'},
            {'type': 'file', 'name': 'decimal_intuition', 'display_name': 'Decimal Intuition'},
            {'type': 'file', 'name': 'long_division', 'display_name': 'Long Division'},
            {'type': 'file', 'name': 'dividing_fractions', 'display_name': 'Dividing Fractions'},
            {'type': 'file', 'name': 'gcf_trees_(easy)', 'display_name': 'GCF Trees (easy)'},
            {'type': 'file', 'name': 'gcf_trees_(difficult)', 'display_name': 'GCF Trees (difficult)'},
            {'type': 'file', 'name': 'lcm_water_pour', 'display_name': 'LCM Water Pour'},
            {'type': 'file', 'name': 'estimating_ratios', 'display_name': 'Estimating Ratios'},
            {'type': 'file', 'name': 'ratio_grouping', 'display_name': 'Ratio Grouping'},
            {'type': 'file', 'name': 'visualizing_ratios', 'display_name': 'Visualizing Ratios'},
            {'type': 'file', 'name': 'comparing_ratios', 'display_name': 'Comparing Ratios'},
            {'type': 'file', 'name': 'racing_ratios', 'display_name': 'Racing Ratios'},
            {'type': 'file', 'name': 'making_unit_ratios', 'display_name': 'Making Unit Ratios'},
            {'type': 'file', 'name': 'ratio_tables', 'display_name': 'Ratio Rables'},
            {'type': 'file', 'name': 'connect_the_dots', 'display_name': 'Connect the Dots'},
        ]
    },
    
    {
        'type': 'folder',
        'name': 'algebra',
        'display_name': 'Algebra',
        'puzzle_list': [
            {'type': 'file', 'name': 'simplifying_expressions', 'display_name': 'Simplifying Expressions'},
            {'type': 'file', 'name': 'evaluating_expressions', 'display_name': 'Evaluating Expressions'},
            {'type': 'file', 'name': 'predicting_linear_equations', 'display_name': 'Predicting Linear Equations'},
            {'type': 'file', 'name': 'algebra_scales', 'display_name': 'Algebra Scales'},
            {'type': 'file', 'name': 'systems_grid', 'display_name': 'Systems Grid'},
        ]
    },

    {
        'type': 'folder',
        'name': 'calculus',
        'display_name': 'Calculus',
        'puzzle_list': [
            {'type': 'file', 'name': 'derivative_zooming', 'display_name': 'Derivative Zooming'},
            {'type': 'file', 'name': 'derivative_drive', 'display_name': 'Derivative Drive'},
            {'type': 'file', 'name': 'f_and_f_prime', 'display_name': 'F and F Prime'},
        ]
    },

    {
        'type': 'folder',
        'name': 'geometry',
        'display_name': 'Geometry',
        'puzzle_list': [
            {'type': 'file', 'name': 'rectilineal_area', 'display_name': 'Rectilineal Area'},
            {'type': 'folder', 'name': 'euclid_constructions_i', 'display_name': 'Euclid Constructions I', 'puzzle_list': [
                {'type': 'file', 'name': 'euclid_constructions_ia', 'display_name': 'Euclid Constructions I (Part A)', 'image_name': 'euclid'},
                {'type': 'file', 'name': 'euclid_constructions_ib', 'display_name': 'Euclid Constructions I (Part B)', 'image_name': 'euclid'},
                {'type': 'file', 'name': 'euclid_constructions_ic', 'display_name': 'Euclid Constructions I (Part C)', 'image_name': 'euclid'},
                {'type': 'file', 'name': 'euclid_constructions_id', 'display_name': 'Euclid Constructions I (Part D)', 'image_name': 'euclid'},
                {'type': 'file', 'name': 'euclid_constructions_ie', 'display_name': 'Euclid Constructions I (Part E)', 'image_name': 'euclid'},
                {'type': 'file', 'name': 'euclid_constructions_if', 'display_name': 'Euclid Constructions I (Part F)', 'image_name': 'euclid'},
                {'type': 'file', 'name': 'euclid_constructions_ig', 'display_name': 'Euclid Constructions I (Part G)', 'image_name': 'euclid'},
            ]},
        ]
    },

    {
        'type': 'folder',
        'name': 'statistics',
        'display_name': 'Statistics',
        'puzzle_list': [
            {'type': 'file', 'name': 'stats_sampling', 'display_name': 'Stats Sampling'},
        ]
    },

    {
        'type': 'folder',
        'name': 'math_challenges',
        'display_name': 'Math Challenges',
        'puzzle_list': [
            {'type': 'file', 'name': 'triangle_sums_(easy)', 'display_name': 'Triangle Sums (easy)'},
            {'type': 'file', 'name': 'triangle_sums_(difficult)', 'display_name': 'Triangle Sums (difficult)'},
            {'type': 'file', 'name': 'what_comes_next', 'display_name': 'What Comes Next?'},
            {'type': 'file', 'name': 'pi_challenge', 'display_name': 'Pi Challenge', 'image_name': 'pi'},
            {'type': 'file', 'name': 'expert_pi_challenge', 'display_name': 'Expert Pi Challenge', 'image_name': 'pi'},
        ]
    },

    {
        'type': 'folder',
        'name': 'coding',
        'display_name': 'Coding',
        'puzzle_list': [
            {'type': 'file', 'name': 'if_else_branching', 'display_name': 'If Else Branching'},
            {'type': 'file', 'name': 'nba_queries', 'display_name': 'NBA Queries'},
            {'type': 'file', 'name': 'n-gram_language_models', 'display_name': 'n-Gram Language Models'},
        ]
    },

    {
        'type': 'folder',
        'name': 'geography',
        'display_name': 'Geography',
        'puzzle_list': [
            {'type': 'file', 'name': 'globe_locate', 'display_name': 'Globe Locate', 'template_dict_function': get_geo_meta},
        ]
    },

    {
        'type': 'folder',
        'name': 'reading',
        'display_name': 'Reading',
        'puzzle_list': [
            {'type': 'file', 'name': 'cloze_wikipedia', 'display_name': 'Cloze Wikipedia'},
            {'type': 'file', 'name': 'cloze_spanish_reader', 'display_name': 'Cloze Spanish Reader'},
        ]
    },

]