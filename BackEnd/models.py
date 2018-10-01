from django.db import models

class Repo(models.Model):
    username = models.CharField(max_length=255)
    reponame = models.CharField(max_length=255)
    ipfs_hash = models.CharField(max_length=255)
    create_time = models.DateTimeField()

    def __str__(self):
        return self.username
    class Meta:
        db_table = "repo"


class Authority(models.Model):
    username = models.CharField(max_length=255)
    repo_id = models.IntegerField()
    user_type = models.CharField(max_length=255, default="owner")
    create_time = models.DateTimeField()

    def __str__(self):
        return self.username
    class Meta:
        db_table = "authority"