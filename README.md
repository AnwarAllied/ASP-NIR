# Django website for ASP-NIR
Website for ASP NIR Analysis.

## Setting up the local server for this project (in a development mode):
This section is for setting up a new local server envirnment for this project in Linux.
1. Make sure python 3 is installed by typing "python" or "python3".
2. Install pipenv for the virtual envirnment:
```
pip install pipenv
```
3. Install and configurate git for github.
4. clone the project:
```
git clone git@github.com:AnwarAllied/ASP-NIR.git
```
5. lunch the virtual envirnment using pipenv (make sure you are in the main ptoject directory where requirements.txt):
```
pipenv shell
```
6. Make sure requirements.txt are instuled.
7. lunch the project:
```
python manage.py runserver
```
8. Test the server on the PC (http://127.0.0.1:8000/).
9. reLunch the project to the local host:
```
python manage.py runserver 0.0.0.0:8000
```

## Setting up the envirnment:
This section is for setting up a new envirnment for this project in Linux.

### Setting up GitHub
#### Commands:
```
sudo apt-get install git
git config --global user.name "anwar"
git config --global user.email "AFallatah@alliedscientificpro.com"
git clone git@github.com:AnwarAllied/ASP-NIR.git
eval $(ssh-agent)
ssh-add 
git pull
touch .gitignore
git rm --cached Pipfile.lock
git checkout -b "spectra_modeling"
```

#### reference:
* [Atlassian](https://www.atlassian.com/git/tutorials/setting-up-a-repository)
* https://docs.gitlab.com/ee/gitlab-basics/start-using-git.html
* https://guides.github.com/features/mastering-markdown/
* https://www.pluralsight.com/guides/how-to-use-gitignore-file

### Setting up SSH:
#### Commands:
```
ssh-keygen -t rsa -b 4096 -C "AFallatah@alliedscientificpro.com"
cat ~/.ssh/id_rsa.pub

```
#### reference:
* https://linuxize.com/post/how-to-set-up-ssh-keys-on-ubuntu-1804/
* https://www.digitalocean.com/community/questions/copy-ssh-key-to-clipboard


### Setting up the vertual envirnment "PIPENV":

#### Commands:
```
pip install pipenv
pipenv --three
pipenv shell
pipenv install Django
pipenv run pip freeze
```
#### reference:
* https://pipenv-fork.readthedocs.io/en/latest/install.html
* https://pipenv-fork.readthedocs.io/en/latest/basics.html

### Setting up Heroku:
* create new account in Heroku: nirvascan
* for installing Heroku in WSL  (Windows with Linux):
```
curl https://cli-assets.heroku.com/install.sh | sh
```
* add Procfile file with:
```
web: gunicorn ASP_NIR.wsgi
```
* add runtime.txt file with:
```
python-3.8.3
```
* add the following to the top & buttom of settings.py:
```
import django_heroku
.
.
.
django_heroku.settings(locals())
```
#### Commands:
```
heroku login
pipenv install gunicorn
sudo apt-get install -y libpq-dev
pipenv install django-heroku
heroku git:remote -a nirvascan
git push heroku predict_model:master
heroku run python manage.py makemigrations
heroku run python manage.py migrate
heroku buildpacks
heroku ps
heroku ps:stop run.9768
heroku logs --tail

```
#### reference:
* https://www.analyticsvidhya.com/blog/2020/10/step-by-step-guide-for-deploying-a-django-application-using-heroku-for-free/
* https://dev.to/wrightdotclick/heroku-cli-on-wsl-26fp
* https://devcenter.heroku.com/categories/python-support
* https://devcenter.heroku.com/articles/git

### Setting up Django:

#### Commands:
```
python -m django --version
django-admin startproject ASP_NIR
python manage.py runserver
python manage.py startapp core
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
from django.contrib.auth.models import User
```
#### reference:
* https://docs.djangoproject.com/en/3.1/intro/tutorial01/
* https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models

## Startting the Core App:
### Copy Admn Site format for the App:
#### Command:

```
admin.site._registry
```

#### referance:
* https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#admin-overriding-templates
* https://docs.djangoproject.com/en/3.1/ref/contrib/admin/actions/
* https://django-matplotlib.readthedocs.io/en/latest/
* https://medium.com/@MicroPyramid/how-to-customize-the-admin-actions-in-list-pages-of-django-admin-f858f326f0ee
* https://github.com/scidam/django_matplotlib/blob/master/django_matplotlib/fields.py
* https://docs.djangoproject.com/en/3.1/topics/forms/formsets/


### upload initial data to the db:
#### Command:
```
python manage.py loaddata core/fixtures.json
```
#### referance:
* https://docs.djangoproject.com/en/3.1/howto/initial-data/