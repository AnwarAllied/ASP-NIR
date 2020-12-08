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
```

#### reference:
* [Atlassian](https://www.atlassian.com/git/tutorials/setting-up-a-repository)
* https://docs.gitlab.com/ee/gitlab-basics/start-using-git.html
* https://guides.github.com/features/mastering-markdown/

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
```
#### reference:
* https://pipenv-fork.readthedocs.io/en/latest/install.html

### Setting up Django:

#### Commands:
```
python -m django --version
django-admin startproject ASP_NIR
python manage.py runserver
python manage.py startapp core
```
#### reference:
* https://docs.djangoproject.com/en/3.1/intro/tutorial01/