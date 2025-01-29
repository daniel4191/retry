from django.db import models
from django.contrib.auth.models import User

import os

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    # admin 단에서의 이름을 설정
    class Meta:
        verbose_name_plural = "Categories"


class Post(models.Model):
    title = models.CharField(max_length=30)
    # 후킹해주는 메세지 100글자 한도로 노출
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    # auto_now=True를 해주면, 추가로 입력해줄 것 없이, 해당되는 내용이 자동 등록 된다.
    # settings에 MEDIA_URL, MEDIA_ROOT로 넣어주었던 주소 뒤로 어떻게 해줄지를 말해준다.
    head_image = models.ImageField(upload_to="blog/images/%Y/%m/%d/", blank=True)
    file_upload = models.FileField(upload_to="blog/files/%Y/%m/%d/", blank=True)

    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    # CASCADE는 연결되어있는 값도 같이 삭제 해준다는 뜻
    # SET_NULL은 해당 값을 삭제해도, 해당 pk 값은 공백으로 두되, 나머지 데이터는 살려두는 것
    # blank=True를 해줘야 카테고리 미 추가시 오류가 뜨지 않는다.
    author = models.ForeignKey(User, null=True, blank=True, on_delete = models.SET_NULL)
    
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

    # 이걸로써, 관리자 단에서 내용을 보게 되면 작성된 텍스트로 표시된다.
    def __str__(self):
        return f"[{self.pk}]{self.title} :: {self.author}"

    def get_absolute_url(self):
        return f"/blog/{self.pk}/"

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)
    
    def get_file_ext(self):
        return self.get_file_name().split(".")[-1]
    