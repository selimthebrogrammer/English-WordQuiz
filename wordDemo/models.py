from django.db import models

# Create your models here.


class Kullanicibilgileri(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=75, blank=True, null=True)
    surname = models.CharField(max_length=75, blank=True, null=True)
    username = models.CharField(max_length=75, blank=True, null=True)
    user_mail = models.CharField(max_length=45, blank=True, null=True)
    user_password = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'kullanicibilgileri'




class Words(models.Model):
    word_id = models.AutoField(primary_key=True)
    word = models.CharField(max_length=63, blank=True, null=True)
    true_word = models.CharField(max_length=63, blank=True, null=True)
    false_word1 = models.CharField(max_length=63, blank=True, null=True)
    false_word2 = models.CharField(max_length=63, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'words'
        
    def __str__(self):
        return self.word



class CorrectAnswers(models.Model):
    correct_answers_i_d = models.AutoField(db_column='correct_answers_id', primary_key=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    word_id = models.IntegerField(blank=True, null=True)
    true_word = models.CharField(max_length=63, blank=True, null=True)
    answer_date = models.DateField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    next_date = models.DateField(blank=True, null=True)
    correct_count = models.IntegerField(blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'correct_answers'
