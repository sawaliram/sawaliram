# Sawaliram
Sawaliram is an online respository of questions asked by school students, collected from across India and answered by experts. The questions are collected with the aim of providing credible answers, fostering curiosity among students of all ages and analysing the questions to gain insights into Indian students' interests and motivations. The project is collaborative between TIFR (Tata Institute of Fundamental Research) Centre for Interdisciplinary Sciences (TCIS), Hyderabad and Eklavya, an NGO based in Bhopal, Madhya Pradesh, which traces its origins to the 'Hoshangabad Science Teaching Program' of 1972-2002.

Apart from the questions and their answers, the web platform will host blog posts, research papers and other resources (like links to relevant books and online media) related to education, pedagogy, questioning and related topics. The website aims to become an invaluable resource to students, teachers, parents, researchers, curriculum designers and other stakeholders.

## Setting up your development environment
To find help with the setup procedure and to discuss all things related to the development, [join our Zulip server](https://sawaliram.zulipchat.com/join/eapx8841i41gyg6ildlpz2t1/).  
  
**1. Install an environment manager**  
It is recommended to use an environment management tool like [virtualenv](https://virtualenv.pypa.io/en/stable/) to easily manage the project's requirements and avoid any conflicts with your system packages. If you are using virtualenv, run these commands to set up a development environment:
```sh
$ cd into/your/project/folder
$ virtualenv -p python3 env
$ source env/bin/activate
```
This will activate an empty virtual environment. You can use ```deactivate``` to exit the environment.

**2. Fork the project**  
Click on the 'Fork' button on the top right corner of this page to create a 'copy' of this project for yourself, on your GitHub profile. You will keep this fork updated with the 'upstream' repository, the one you're at now. You will also create branches on your own fork before sending a Pull Request to the upstream repo.  

**3. Set up a git repository for your system**  
Run these commands to set up a local git repository and populate with the code you just forked:
```sh
$ mkdir code
$ cd code
$ git init
$ git remote add upstream https://github.com/tifrh/sawaliram.git
$ git remote add origin https://github.com/your-username/sawaliram.git
$ git pull origin master
```
At this point, your project folder will have an `env` directory for your virtual environment, and a `code` directory for your code.

**4. Install dependencies**  
In the root folder (where the requirements.txt file is), run this command to install all dependencies:
```sh
$ pip install -r requirements.txt
```
**5. Initialize the database**  
The project uses PostgreSQL as its database. If you haven't set up a PostgreSQL server on your system, follow [this](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04) or [this](http://www.marinamele.com/taskbuster-django-tutorial/install-and-configure-posgresql-for-django) resource to set it up.
Once you have your database up and running, apply the migrations for the data models by running the following command in the root directory:
```sh
$ python manage.py migrate
```
**6. Add environment variables to your shell**  
The project reads some values for configuring the project from the local environment variables. To permanently add variables to the shell environment, add these lines to the ```.bash_profile``` file in your home directory (for Linux and MacOS users):
```sh
export sawaliram_secret_key='some_string_without_spaces'
export sawaliram_debug_value='True'
export sawaliram_db_password='your-database-password'
export environment='dev'
```
To generate a secret key, you can use the Django's built-in `get_random_secret_key()` function:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
After saving the file, make sure you run ```$ source .bash_profile``` to save the changes to your existing bash session. The instructions for Windows might be different.

**7. Run scripts to finish the setup**  
To perform the remaining updation or configuration, run these commands:
```sh
$ python manage.py createusergroups
$ python manage.py createsubmissionsfolder
```

**8. Run the test server**  
To test your setup and to make sure everything is working as expected, run the test server from the root directory (where you can find the `manage.py` file):
```sh
python manage.py runserver
```
Visit localhost:8000 in your browser to see the Sawaliram homepage in all it's glory!

You are now ready to write some code! Begin by reading our [contributing guide](https://github.com/tifrh/sawaliram/blob/master/contributing.md) to help you get started!
