from django.db import models
import numpy as np

class StaticModel(models.Model):
    name=models.CharField(max_length=60)
    component = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name

    def comp(self):
        return np.array(eval("["+self.component+"]"))

    class Meta:
        verbose_name = 'Static Model'
        verbose_name_plural = "Static Models"


class IngredientsModel(models.Model):
    name = models.CharField(max_length=60)
    component = models.CharField(max_length=3)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ingredients Model'
        verbose_name_plural = "Ingredients Models"

