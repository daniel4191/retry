from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category
from django.db.models import Count

class PostList(ListView):
    model = Post
    ordering = "-pk"
    # template_name = "blog/index.html"

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context["categories"] = Category.objects.annotate(post_count=Count('post'))
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        # context["category"] = None
        return context
        

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context["categories"] = Category.objects.annotate(post_count=Count('post'))
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        return context

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "hook_text", "content", "head_image", "file_upload", "category"]

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated:
            form.instance.author = current_user
            return super(PostCreate, self).form_valid(form)
        else:
            return redirect("/blog/")
            

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