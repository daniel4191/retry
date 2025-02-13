from django.shortcuts import render
from blog.models import Post

# Create your views here.
def landing(request):
    # 최근 포스트 노출 준비
    recent_posts = Post.objects.order_by("-pk")[:3]
    return render(
        request, "single_pages/landing.html",
        {
            "recent_posts" : recent_posts
        }
        )

def about_me(request):
    return render(
        request, "single_pages/about_me.html"
        )

        