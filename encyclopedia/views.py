from django.shortcuts import render
from . import util
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from random import choice

import markdown2

# ====================================================================== Classes
class SearchBar(forms.Form):
    inputField = forms.CharField(
        label = "",
        max_length = 70,
        widget = forms.TextInput(
            attrs = {
                'class': 'search',
                'placeholder': 'Search Beer'
            }
        )
    )

class NewPage(forms.Form):
    title = forms.CharField(
        label = "",
        min_length = 2,
        max_length = 70,
        widget = forms.Textarea(
            attrs = {
                'class': 'titlebox',
                'placeholder': 'Enter here the title...'
            }
        )
    )
    content = forms.CharField(
        label = "",
        min_length = 5,
        widget = forms.Textarea(
            attrs = {
                'class': 'contentbox',
                'placeholder': 'Enter here the content...',
            }
        )
    )

class EditPage(forms.Form):
    content = forms.CharField(
        label = "",
        min_length = 5,
        widget = forms.Textarea(
            attrs = {'class': 'contentbox',}
        )
    )

# ======================================================================== Index
def index(request):
    # Replace "_" by " " in the displayed list (entriesNames), but not in the
    # hyperlinks/filenames (entries)
    entries = util.list_entries()
    entriesNames = []

    for entry in entries:
        entriesNames.append(entry.replace("_", " "))

    return render(request, "encyclopedia/index.html", {
        "form": SearchBar(),
        "entries": zip(entries, entriesNames),
        "title": "All Pages"
    })


# ========================================================================= Page
def page(request, title):
    if title in util.list_entries():
        return render(request, "encyclopedia/page.html", {
            "form": SearchBar(),
            # Diplay the title without underscores
            "displaytitle": title.replace("_", " "),
            "title": title,
            "content": markdown2.markdown(util.get_entry(title))
        })

    else:
        return HttpResponseRedirect(reverse("error", args=["404", title]))


# ====================================================== Search engine in layout
def searchField(request):
    if request.method == "POST":
        form = SearchBar(request.POST)

        if form.is_valid():
            title = form.cleaned_data["inputField"]

            # Making search case insensitive by casefolding user's input AND items
            # from the list_entries, using List Comprehension.
            listEntries = util.list_entries()
            caseFoldedFilename = [filename.casefold() for filename in listEntries]

            # Finds full match
            if title.casefold().replace(" ", "_") in caseFoldedFilename:
                positionList = caseFoldedFilename.index(title.casefold().replace(" ", "_"))
                # Use the position in the list as an argument
                return HttpResponseRedirect(reverse('page', args = [listEntries[positionList]]))

            # Finds partial match
            elif (substrings := [listEntries[i] for i, x in enumerate(caseFoldedFilename) if title.casefold() in x]):
                # Replace "_" by " " in the displayed list (entriesNames), but not in the
                # hyperlinks/filenames (entries)
                entries = substrings
                entriesNames = []

                for entry in entries:
                    entriesNames.append(entry.replace("_", " "))

                return render(request, "encyclopedia/index.html", {
                    "form": SearchBar(),
                    "entries":zip(entries, entriesNames),
                    "title": 'Search results for "' + title + '"'
                })

            # Finds no match
            else:
                return HttpResponseRedirect(reverse("error", args=["404", title]))

    return HttpResponseRedirect(reverse("index"))


# ========================================================================== New
def new(request):
    if request.method == "POST":
        newPage = NewPage(request.POST)

        if newPage.is_valid():
            # Save title with underscores instead of blanks
            title = newPage.cleaned_data["title"].replace(" ", "_")
            content = newPage.cleaned_data["content"]
            caseFoldedFilename = [filename.casefold() for filename in util.list_entries()]

            if title.casefold() in caseFoldedFilename:
                return HttpResponseRedirect(reverse("error", args=["duplicate", title]))

            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('page', args=[title]))

    return render(request, "encyclopedia/new.html", {
        "form": SearchBar(),
        "newpage": NewPage(),
        "title": "Create New Page",
        "newOrEdit": reverse("new")
    })


# ========================================================================= Edit
def edit(request, title):
    if request.method == "POST":
        newPage = EditPage(request.POST)

        if newPage.is_valid():
            content = newPage.cleaned_data["content"]

            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('page', args=[title]))

    newpageform = EditPage()
    newpageform["content"].initial = util.get_entry(title)

    return render(request, "encyclopedia/new.html", {
        "form": SearchBar(),
        "newpage": newpageform,
        "title": "Edit " + title.replace("_", " "),
        "newOrEdit": reverse("edit", kwargs={'title': title})
    })


# ======================================================================= Random
def random(request):
    entries = util.list_entries()
    randomPage = choice(entries)
    return HttpResponseRedirect(reverse('page', args=[randomPage]))


# ======================================================================== Error
def error(request, errortype, title):
    if errortype == "404":
        errorMessage = '"' + title + '" not found.'
    elif errortype == "duplicate":
        errorMessage = '"' + title.replace("_", " ") + '" already exists.'
    return render(request, "encyclopedia/error.html", {
        "form": SearchBar(),
        "errorMessage": errorMessage
    })
