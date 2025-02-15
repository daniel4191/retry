from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.db.models import Count
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from django.db.models import Q

import re

class PostList(ListView):
    model = Post
    ordering = "-pk"
    # template_name = "blog/index.html"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        # context["categories"] = Category.objects.annotate(post_count=Count('post'))
        context["categories"] = Category.objects.all()
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        # context["category"] = None
        return context
        

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(post_count=Count('post'))
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        context["comment_form"] = CommentForm()
        return context

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response

        else:
                return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(
                    name=t,
                    defaults={"slug": slugify(t, allow_unicode=True)} # 추가
                    )
                # if is_tag_created:
                #     tag.slug = slugify(t, allow_unicode=True)
                #     tag.save()
                self.object.tags.add(tag)

        return response

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model =Comment
    form_class = CommentForm

    # 이 메서드를 이용해서 같은 주소라도 작성한 유저가 같은지를 필터한다.
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


class PostSearch(PostList):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs["q"]
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)
        ).distinct()
        return post_list

    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs["q"]
        context["search_info"] = f"Search: {q} ({self.get_queryset().count()})"

        return context

# Create your views here.
# def index(request):
#     #  order_by를 -로 해놓으면 역순의 개념이 되는 것이고, 기준값은 pk 즉, 여기서는 생성된 글의 넘버다.
#     posts = Post.objects.all().order_by("-pk")

#     return render(
#         request, "blog/index.html",
#         {
#             "posts":posts
#         }
#     )


# FBV style



def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(
        request, "blog/single_post_page.html",
        {
            "post":post
        }
    )

def category_page(request, slug):
    if slug == "no_category":
        category = None
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        "blog/post_list.html",
        {
            "post_list": post_list,
            "categories": Category.objects.annotate(post_count=Count('post')),
            "no_category_post_count": Post.objects.filter(category=None).count(),
            "category": category
        }
    )

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()
    
    return render(
        request,
        "blog/post_list.html",
        {
            "post_list": post_list,
            "tag" : tag,
            "categories" : Category.objects.annotate(post_count=Count('post')),
            "no_category_post_count" : Post.objects.filter(category=None).count()
        }
    )

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if request.method == "POST":
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(post.get_absolute_url())
            else:
                return redirect(post.get_absolute_url())

        else:
            raise PermissionDenied


def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied