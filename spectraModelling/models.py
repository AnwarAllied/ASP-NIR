from django.db.models.signals import post_save
from django.db import models
from core.models import Spectrum
import numpy as np
from scipy import signal

# defult Spectrum setting:
start= 901.4908633          # Start wavelength (nm):	900
end= 1701.221829            # End wavelength (nm):	1700
steps= 3.5230439017621147   # Pattern Pixel Width (nm):	7.03
wavelength_length= 228

# pr=np.polyfit(range(228),y,2)
x_param=[-2.51856723e-03,  4.09427539e+00,  9.01322866e+02]


def get_x_poly():
    p=np.poly1d(param)
    best_fit=p(range(228))
    return best_fit

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

    def __str__(self):
        return self.spectrum.slug()+' model'

    def slug(self):
        return self.spectrum.slug()+'_poly'

    def x(self):
        return self.spectrum.x()

    def y(self):
        return np.array(eval("["+self.y_axis+"]"))
        
    def get_absolute_url(self):
        return reverse("spectraModelling", kwargs={
            'slug': self.slug()
        })

    def norm(self):
        y=self.spectrum.y()
        mx=max(y)
        mi=min(y)
        return np.array(((y-mi)/(mx-mi)).tolist())

    def obtain(self):
        ms=1;pm=50
        df=pm-ms;ordr=4
        yn=self.norm()
        x=self.spectrum.x()
        while True:  #(df > 1e-8) and ms>.005:
            if (df > 1e-8) and (ms<.005 or ordr>18):
                break
            param=np.polyfit(x, yn, ordr)
            p = np.poly1d(param)
            ft=p(x)
            ms=np.mean(yn**2-ft**2)
            df=(ms-pm)**2
            ordr+=1
            pm=ms.copy()

        self.order=ordr
        self.mse=ms
        self.parameter=str(param.tolist())[1:-1]
        self.y_axis=str(ft.tolist())[1:-1]

# auto create and save poly whenever Spectrum created.
def poly_receiver(sender, instance, created, *args, **kwargs):
    if created:
        poly = Poly(spectrum = instance)
        poly.obtain()
        poly.save()
        print(poly.slug()+' created & saved successfully')

post_save.connect(poly_receiver, sender=Spectrum)

def poly_for_all(m):
    for i in Spectrum.objects.all()[0:m]:
        poly=Poly(spectrum = i)
        poly.obtain()
        # poly.save()
        print(poly.slug()+' created & saved successfully')

def fft_sampling(y):
    return signal.resample(y, wavelength_length)
    

# from spectraModelling.models import Poly
# from spectraModelling.models import poly_for_all as pa
# from core.models import Spectrum
# po=Poly(spectrum = Spectrum.objects.get(id=55))
# po.obtain()