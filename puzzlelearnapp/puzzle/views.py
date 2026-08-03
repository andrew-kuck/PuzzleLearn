from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
import json
from .view_functions.geography import get_random_city_with_address, get_random_city_with_address_filtered, get_random_city_with_address_major_cities
from .view_functions.puzzle_list import puzzle_list
from.view_functions.utils import clean_display_list
from django.http import HttpResponse, JsonResponse, Http404
from urllib.parse import urlparse
import requests
import copy


def index(request):
    display_list = clean_display_list(copy.deepcopy(puzzle_list))
    return render(request, 'puzzle/index.html', {'display_list': display_list})


def page(request, url_path):
    url_args = url_path.lower().strip('/').split('/')
    display_list = copy.deepcopy(puzzle_list)
    for url_arg in url_args:
        valid_url = False
        for item in display_list:
            if item['name'] == url_arg:
                valid_url = True
                if item['type'] == 'folder':
                    display_list = item['puzzle_list']
                    break
                elif item['type'] == 'file':
                    html_file_path = f"puzzle/puzzles/{url_path.strip('/')}.html"
                    template_dict = {'puzzle_name': item['display_name']}
                    if item.get('template_dict_function'):
                        template_dict = template_dict | item['template_dict_function']()
                    return render(request, html_file_path, template_dict)
        if not valid_url:
            raise Http404("We could not find that page.")
    display_list = clean_display_list(display_list)
    return render(request, 'puzzle/index.html', {'display_list': display_list})



@require_POST
def get_geo_data(request):
    globe_location = {}
    payload = {}
    if request.content_type == 'application/json':
        payload = json.loads(request.body)
    else:
        payload = {k: v for k, v in request.POST.items()}

    if payload.get('mode') == 'major_cities':
        globe_location = get_random_city_with_address_major_cities()
    elif len(payload) == 0:
        globe_location = get_random_city_with_address()
    else:
        globe_location = get_random_city_with_address_filtered(payload)
    return JsonResponse(globe_location)


@require_POST
def generate_nba_question(request):
    
    from .view_functions.nba import generate_question_with_ollama, generate_fallback_question
    payload = json.loads(request.body)

    columns = payload.get("columns", [])
    sample_rows = payload.get("sampleRows", [])

    try:
        question = generate_question_with_ollama(columns, sample_rows)
        return JsonResponse(question)
    except Exception:
        fallback = generate_fallback_question(sample_rows)
        return JsonResponse(fallback)
    

ALLOWED_GUTENBERG_HOSTS = {
    "www.gutenberg.org",
    "gutenberg.org",
    "gutendex.com",
}


def is_allowed_gutenberg_url(url):
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in {"http", "https"}
            and parsed.netloc in ALLOWED_GUTENBERG_HOSTS
        )
    except Exception:
        return False


@require_GET
def fetch_gutenberg_text(request):
    url = request.GET.get("url")

    if not url:
        return JsonResponse({"error": "Missing URL."}, status=400)

    if not is_allowed_gutenberg_url(url):
        return JsonResponse({"error": "Unsupported URL."}, status=400)

    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Django Gutenberg N-Gram Educational Activity"
            },
        )

        if response.status_code != 200:
            return JsonResponse(
                {
                    "error": f"Could not fetch Gutenberg text. Status: {response.status_code}"
                },
                status=response.status_code,
            )

        return HttpResponse(
            response.text,
            content_type="text/plain; charset=utf-8",
        )

    except requests.RequestException as error:
        return JsonResponse({"error": str(error)}, status=500)
