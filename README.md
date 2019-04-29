# Sawaliram
Sawaliram is an online platform built to collect, answer and analyze questions asked by school students across India. It is developed and maintained by TIFR Centre for Interdisciplinary Sciences, Hyderabad and Eklavya, Bhopal. The current development focuses on building a dashboard to collect and answer questions, including tools to moderate and correct the data.

## Setting up your development environment
**1. Install an environment manager**  
It is recommended to use an environment management tool like [virtualenv](https://virtualenv.pypa.io/en/stable/) to easily manage the project's requirements and avoid any conflicts with your system packages. If you are using virtualenv, run these commands to set up a development environment:
```sh
$ cd into/your/project/folder
$ virtualenv -p python3 env
$ source env/bin/activate
```
This will activate an empty environment. You can use ```deactivate``` to exit the environment.

**2. Fork the project**  
Click on the 'Fork' button on the top right corner of this page the create a 'copy' of this project for yourself. You will keep this fork updated with the 'upstream' repository, the one you're at now. You will also create branches on your own fork before sending a Pull Request to the upstream repo.  

**3. Set up a git repository for your system**  
Run these commands to set up a local git repository and populate with the code you just forked:
```sh
$ mkdir code
$ cd code
$ git init
$ git remote add origin https://github.com/tifrh/sawaliram.git
$ git pull origin master
```

**4. Install dependencies**  
In the root folder (where the requirements.txt file is), run this command to install all dependencies:
```bash
$ pip install -r requirements.txt
```

You will also need to install [memcached](https://memcached.org) and [RabbitMQ](https://rabbitmq.com) for caching and scheduling functionality. You can probably install them via your package manager using something like
```bash
$ sudo apt-get install rabbit-server memcached
```

**5. Add environment variables to your shell**  
The project reads some values for the configuration from the environment variables. To permanently add variables to the shell environment, add this line to the ```.bash_profile``` file:
```sh
export sawaliram_secret_key='some_string_without_spaces'
export sawaliram_debug_value='True'
export sawaliram_db_password='your-password'
export environment='dev'
```

You can also add optional RabbitMQ configuration variables, like so:
```sh
export sawaliram_rabbitmq_username='you-username'
export sawaliram_rabbitmq_password='your-password'
export sawaliram_rabbitmq_host='your-hostname'
```
If you do not set these, then default values of `sawaliram`, `pass`, and `sawaliram` will be used instead.

After saving the file, make sure you run ```$ source .bash_profile``` to save the changes to your existing bash session.

**6. Initialize the database**  
The project uses PostgreSQL as its database. If you haven't set up a PostgreSQL server on your system, follow [this](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04) or [this](http://www.marinamele.com/taskbuster-django-tutorial/install-and-configure-posgresql-for-django) resource to set it up.
Once you have your database up and running, apply the migrations for the data models by running the following command in the root directory:
```bash
$ python manage.py migrate
```

**7. Run scripts to finish the setup**  
To perform the remaining updation or configuration, run these commands:
```bash
$ python manage.py createusergroups
```

**8. Running the server**
To run the test development server, use the command
```bash
$ python manage.py runserver
```
Similarly, the Celery task runner can be run using
```bash
$ celery -A core worker -l info -B # FOR DEVELOPMENT ONLY
```
For production settings, it is recommended to run the task scheduler and the task runner separately. The relevant comands are:
```bash
$ celery -A core worker -l info # Task runner
$ celery -A core beat -l info # Task scheduler
```
All process mentioned in this section can be terminated using the `Ctrl+C` keyboard shortcut.

You are now ready to write some code! Start by looking at the open issues on the repo.
