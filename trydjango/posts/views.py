from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .forms import PostForm
from .models import Post


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        return HttpResponseForbidden()

    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.info(request, "Created!")
        return HttpResponseRedirect(instance.get_absolute_path())

    context = {
        "title": "Create new post",
        "button": "Create",
        "form": form
    }
    return render(request, "post_create.html", context)


def post_detail(request, slug=None):
    context = {
        "obj": get_object_or_404(Post, slug=slug)
    }
    return render(request, "post_detail.html", context)


def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.info(request, "Updated!")
        return HttpResponseRedirect(instance.get_absolute_path())

    context = {
        "title": "Edit post",
        "button": "Save",
        "obj": instance,
        "form": form
    }
    return render(request, "post_create.html", context)


def post_delete(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.info(request, "Deleted!")
    return redirect("posts:list")


def post_list(request):
    q = request.GET.get("q")

    if q:
        queryset = Post.objects.search(q)
    else:
        queryset = Post.objects.list()

    paginator = Paginator(queryset, 5)
    page_get_param = "page"
    page = request.GET.get(page_get_param)

    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(1 if int(page) < 1 else paginator.num_pages)

    context = {
        "object_list": object_list,
        "page_get_param": page_get_param
    }
    return render(request, "post_list.html", context)
