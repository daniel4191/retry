from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    # auto_now=True를 해주면, 추가로 입력해줄 것 없이, 해당되는 내용이 자동 등록 된다.
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    # author - 추후 작성 예정

    # 이걸로써, 관리자 단에서 내용을 보게 되면 작성된 텍스트로 표시된다.
    def __str__(self):
        return f"[{self.pk}] {self.title}"

    def get_absolute_url(self):
        return f"/blog/{self.pk}/"
    