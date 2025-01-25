from django.shortcuts import render
from .models import Post

# Create your views here.
def index(request):
    #  order_by를 -로 해놓으면 역순의 개념이 되는 것이고, 기준값은 pk 즉, 여기서는 생성된 글의 넘버다.
    posts = Post.objects.all().order_by("-pk")

    return render(
        request, "blog/index.html",
        {
            "posts":posts
        }
    )