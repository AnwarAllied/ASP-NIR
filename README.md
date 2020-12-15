# Django website for ASP-NIR
Website for ASP NIR Analysis.

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

### Setting up Django:

#### Commands:
```
python -m django --version
django-admin startproject ASP_NIR
python manage.py runserver
python manage.py startapp core
python manage.py makemigrations
python manage.py migrate
python3 manage.py createsuperuser
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


### upload initial data to the db:
#### Command:
```
python manage.py loaddata core/fixtures.json
```
#### referance:
* https://docs.djangoproject.com/en/3.1/howto/initial-data/
class test:  
    #@staticmethod
    def square(x):  
        test.result = x*x 