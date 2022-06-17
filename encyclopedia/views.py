import logging
import random

from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from . import util
from . import my_forms

# Add logging.
logger_views = logging.getLogger("views")
handler = logging.FileHandler('wiki.log')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(f_format)
logger_views.addHandler(handler)


def get_search_page(request):
    """Get q argument from request.
    If entry exist - returns it page,
    else - returns search result,
    else - returns None.

    """
    get_title = request.GET.get('q', '')
    if get_title:
        existed_entries = util.list_entries()
        # If page exist
        if get_title in existed_entries:
            return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': f'{get_title}'}))
        # Try to search substring
        entries = [entry for entry in existed_entries if get_title.lower() in entry.lower()]
        return render(request, "encyclopedia/search_result.html", {
            "entries": entries,
            "request_article": get_title
        })
    else:
        return None


def index(request):
    render_search = get_search_page(request)
    if render_search:
        return render_search
    else:
        return render(request, "encyclopedia/index.html", {
            "entries": sorted(util.list_entries(), key=lambda x: x.lower())
        })


def entry(request, title):
    """Render entry of encyclopedia where title = title

    """
    render_search = get_search_page(request)
    if render_search:
        return render_search
    else:
        # If title not empty and if it presents in entries.
        if title not in util.list_entries():
            return render(request, "encyclopedia/error.html", {
                "error_msg": f'Page with title "{title}" is not exist.'
            })
        else:

            html_page = util.markdown_converter(util.get_entry(title))
            if html_page:
                return render(request, "encyclopedia/entry.html", {
                    "title": title,
                    "html_page": html_page
                })
            else:
                logger_views.error(f"Can not convert {title} to HTML.")
                return render(request, "encyclopedia/error.html", {
                    "error_msg": f'Please try again.'
                })


def create_new_page(request):
    """Create new page
    """
    if request.method == 'POST':

        form = my_forms.form_new_page(request.POST)
        if form.is_valid():
            # If page already exist
            if form.cleaned_data['title'] in util.list_entries():
                return render(request, 'encyclopedia/error.html', {
                    'error_msg': f'Page "{form.cleaned_data["title"]}" already exists.'
                })
            else:
                title = form.cleaned_data['title']
                content = form.cleaned_data['content']
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': f'{title}'}))
        else:
            logger_views.error(f"Not valid form. {form.data}")
            return render(request, 'encyclopedia/error.html', {
                'error_msg': f'Your form is not valid. Try again.'
            })
    else:
        render_search = get_search_page(request)
        if render_search:
            return render_search
        else:
            form = my_forms.form_new_page()
            return render(request, "encyclopedia/create_edit_page.html", {
                'form': form,
                'title': f"Create page",
                'action': '/wiki/create_page/'
            })


def edit_page(request):
    if request.method == "POST":
        form = my_forms.form_new_page(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('encyclopedia:entry', kwargs={'title': f'{title}'}))
        else:
            logger_views.error(f"Can not edit entry")
            return render(request, 'encyclopedia/error.html', {
                'error_msg': f'Your form is not valid. Try again.'
            })
    else:
        render_search = get_search_page(request)
        if render_search:
            return render_search
        else:
            get_title = request.GET.get('t', '')
            if get_title:
                existed_entries = util.list_entries()
                # If page exist
                if get_title in existed_entries:
                    context = util.get_entry(get_title)
                    form = my_forms.form_edit_page({'title': f'{get_title}', 'content': f'{context}'})

                    return render(request, 'encyclopedia/create_edit_page.html', {
                        'title': f'Edit page {get_title}',
                        'action': '/wiki/edit_page/',
                        'form': form
                    })

            return HttpResponseRedirect(reverse("encyclopedia:index"))


def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return HttpResponseRedirect(reverse("encyclopedia:entry", kwargs={'title': f'{random_entry}'}))
