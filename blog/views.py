# from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Category

class PostList(ListView):
    model = Post
    ordering = "-pk"
    # template_name = "blog/index.html"

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context["categories"] = Category.objects.all()
        context["no_category_post_count"] = Post.objects.filter(category=None).count()
        return context

class PostDetail(DetailView):
    model = Post

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

def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(
        request, "blog/single_post_page.html",
        {
            "post":post
        }
    )