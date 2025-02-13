from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

import os

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/category/{self.slug}/"
    

    # admin 단에서의 이름을 설정
    class Meta:
        verbose_name_plural = "categories"


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/blog/tag/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:  # 슬러그가 없는 경우에만 생성
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    

class Post(models.Model):
    title = models.CharField(max_length=30)
    # 후킹해주는 메세지 100글자 한도로 노출
    hook_text = models.CharField(max_length=100, blank=True)
    content = MarkdownxField() # 텍스트 들여쓰기 등 자동 조정

    # auto_now=True를 해주면, 추가로 입력해줄 것 없이, 해당되는 내용이 자동 등록 된다.
    # settings에 MEDIA_URL, MEDIA_ROOT로 넣어주었던 주소 뒤로 어떻게 해줄지를 말해준다.
    head_image = models.ImageField(upload_to="blog/images/%Y/%m/%d/", blank=True)
    file_upload = models.FileField(upload_to="blog/files/%Y/%m/%d/", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # CASCADE는 연결되어있는 값도 같이 삭제 해준다는 뜻
    # SET_NULL은 해당 값을 삭제해도, 해당 pk 값은 공백으로 두되, 나머지 데이터는 살려두는 것
    # blank=True를 해줘야 카테고리 미 추가시 오류가 뜨지 않는다.
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)

    # 이걸로써, 관리자 단에서 내용을 보게 되면 작성된 텍스트로 표시된다.
    def __str__(self):
        return f"[{self.pk}]{self.title} :: {self.author}"

    def get_absolute_url(self):
        return f"/blog/{self.pk}/"

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)
    
    def get_file_ext(self):
        return self.get_file_name().split(".")[-1]

    def get_content_markdown(self):
        return markdown(self.content)

    def get_absolute_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            f"https://doitdjango.com/avatar/id/1408/e7e3581c91812561/svg/{self.author.email}"
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models. TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.author} :: {self.content}"
    
    def get_absolute_url(self):
        return f"{self.post.get_absolute_url}#comment-{self.pk}"  # 상대 경로로 변경
    
    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f"https://doitdjango.com/avatar/id/1408/e7e3581c91812561/svg/{self.author.email}"