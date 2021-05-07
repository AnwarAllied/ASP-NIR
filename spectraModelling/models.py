from django.db.models.signals import post_save
from django.db import models
from django.urls import reverse

from core.models import Spectrum
import numpy as np
from scipy import signal
from datetime import datetime

# defult Spectrum setting:
start = 901.4908633  # Start wavelength (nm):	900
end = 1701.221829  # End wavelength (nm):	1700
steps = 3.5230439017621147  # Pattern Pixel Width (nm):	7.03
wavelength_length = 228

# pr=np.polyfit(range(228),y,2)
x_param = [-2.51856723e-03, 4.09427539e+00, 9.01322866e+02]


def get_x_poly():
    p = np.poly1d(x_param)
    best_fit = p(range(wavelength_length))
    return best_fit


x_poly = get_x_poly()


class Poly(models.Model):
    y_axis = models.TextField(blank=True, null=True)
    parameter = models.TextField(blank=True, null=True)
    mse = models.FloatField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    spectrum = models.OneToOneField(
        Spectrum,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    similar_pk = models.ManyToManyField('Poly')

    def __str__(self):
        return self.spectrum.slug() + ' model'

    def slug(self):
        return self.spectrum.slug() + '_poly'

    def x(self):
        return x_poly

    def y(self):
        return np.array(eval("[" + self.y_axis + "]"))

    def y_all(self):  # y_axis of all similar spectra
        yn = to_wavelength_length_norm(self.y()).tolist()
        y_similar = [i.y().tolist() for i in self.similar_pk.all() if i.pk != self.pk]
        return np.array([yn] + y_similar)

    def label(self):
        return self.spectrum.origin

    def param(self):
        return np.array(eval("[" + self.parameter + "]"))

    def get_absolute_url(self):
        return reverse("spectraModelling", kwargs={
            'slug': self.slug()
        })

    def obtain(self):
        ms = 1;
        pm = 50
        df = pm - ms;
        ordr = 4
        yn = to_wavelength_length_norm(self.spectrum.y())
        x = x_poly  # self.spectrum.x()
        while True:  # (df > 1e-8) and ms>.005:
            if (df < 1e-8) and (ms < .005 or ordr > 18):
                break
            param = np.polyfit(x, yn, ordr)
            p = np.poly1d(param)
            ft = p(x)
            ms = np.mean(yn ** 2 - ft ** 2)
            df = (ms - pm) ** 2
            ordr += 1
            pm = ms.copy()

            self.order = ordr
            self.mse = ms
            self.parameter = str(param.tolist())[1:-1]
            self.y_axis = str(ft.tolist())[1:-1]

    def update_similar(self):
        param = self.param()
        q = Poly.objects.filter(order=self.order)
        if q:  # incase of avaliable
            pra = [np.mean(np.log(np.abs(i.param() - param))) for i in q]
            if len(pra) > 1:
                sr = np.argsort(pra)[:4]
                self.similar_pk.add(*[q[int(i)] for i in sr])
            elif pra:
                self.similar_pk.add(*[q[int(i)] for i in range(len(pra))])


class Match(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # default = datetime.now() )
    y_axis = models.TextField()
    x_range_max = models.FloatField(blank=True, null=True)
    x_range_min = models.FloatField(blank=True, null=True)
    parameter = models.TextField(blank=True, null=True)
    mse = models.FloatField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    poly = models.ManyToManyField(Poly)

    def __str__(self):
        return str(self.created_at)[:-13]

    def y(self):
        return np.array(eval("[" + self.y_axis + "]"))

    def x(self):
        return x_poly

    def y_all(self):
        yn = to_wavelength_length_norm(self.y()).tolist()
        y_match = [to_wavelength_length_norm(i.spectrum.y()).tolist() for i in self.poly.all()]
        return np.array([yn] + y_match)

    def origin(self):
        return 'Unknown'

    def label(self):
        return self.__str__()

    def param(self):
        return np.array(eval("[" + self.parameter + "]"))

    def obtain(self):
        ms = 1;
        pm = 50
        df = pm - ms;
        ordr = 4
        yn = to_wavelength_length_norm(self.y())
        x = x_poly  # self.spectrum.x()
        while True:  # (df > 1e-8) and ms>.005:
            if (df < 1e-8) and (ms < .005 or ordr > 18):
                break
            param = np.polyfit(x, yn, ordr)
            p = np.poly1d(param)
            ft = p(x)
            ms = np.mean(yn ** 2 - ft ** 2)
            df = (ms - pm) ** 2
            ordr += 1
            pm = ms.copy()
        self.order = ordr
        self.mse = ms
        self.parameter = str(param.tolist())[1:-1]
        q = Poly.objects.filter(order=ordr)
        # self.id=Match.objects.last().id+1
        self.clean()
        self.save()
        if q:  # incase of avaliable
            pra = [np.mean(np.log(np.abs(np.array(i.param() - param)))) for i in q]
            if len(pra) > 1:
                sr = np.argsort(pra)[:3]
                self.poly.add(*[q[int(i)] for i in sr])
            elif pra:
                self.poly.add(*[q[int(i)] for i in range(len(pra))])

    class Meta:
        verbose_name_plural = "Match history"


# auto create and save poly whenever Spectrum created.
def poly_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.y_axis:
        poly = Poly(spectrum=instance)
        poly.obtain()
        poly.save()
        poly.update_similar()
        print(poly.slug() + ' created & saved successfully')


post_save.connect(poly_receiver, sender=Spectrum)


def poly_for_all(m):  # process it one time to get poly of existing spectra
    for i in Spectrum.objects.all()[0:m]:
        poly = Poly(spectrum=i)
        poly.obtain()
        poly.save()
        poly.update_similar()
        print(poly.slug() + ' created & saved successfully')


def poly_update_similar_all(m):  # process it one time to get poly of existing spectra
    for poly in Poly.objects.all()[0:m]:
        poly.update_similar()
        print(poly.slug() + ' created & saved successfully')


def fft_sampling(y):
    return signal.resample(y, wavelength_length)


def norm(yl):
    mx = max(yl)
    mi = min(yl)
    return np.array(((yl - mi) / (mx - mi)).tolist())


def to_wavelength_length_norm(y):
    l = len(y)
    if l != wavelength_length:
        df = l - wavelength_length
        if df > 0:
            x = np.round(np.linspace(0, l - 1, wavelength_length)).astype(int)
            return norm(y[x])
        else:
            return norm(fft_sampling(y))
    else:
        return norm(y)