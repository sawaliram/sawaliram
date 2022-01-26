import fire
import os 
import subprocess


CONTENT_LANGUAGES = [
    ('bn', 'বাংলা'),
    ('en', 'English'),
    ('hi', 'हिंदी'),
    ('mr', 'मराठी'),
    ('ml', 'മലയാളം'),
    ('ta', 'தமிழ்'),
    ('te', 'తెలుగు'),
]

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


langs = ['bn', 'hi', 'mr', 'ml', 'ta', 'te']


def make_po(app, lang):
    if app == 'public_website':
       locale_dir = os.path.abspath(os.path.join(location, 'public_website/'))
    elif app == 'dashboard':
        locale_dir = os.path.realpath(os.path.join(location, "dashboard/"))
    elif app == "sawaliram_auth":
        locale_dir = os.path.abspath(os.path.join(location, "sawaliram_auth/"))

    else:
        raise Exception("Please enter valid app name of sawaliram project")

    if not os.path.exists(locale_dir):
        os.makedirs(locale_dir)
    else:
        os.path.join(locale_dir)


    if lang in langs:
        com = "python3 ../manage.py makemessages -l " + lang
        subprocess.run(com, cwd=locale_dir,shell=True)
    elif lang == "all":
         for i in langs:
             subprocess.run("python3 ../manage.py makemessages -l "+i, cwd=locale_dir,shell=True)

    else:
        raise Exception("Please enter valid language code")
    
    print(">>>  Mission completed all PO files generated!   <<<")



if __name__ == "__main__":
    fire.Fire(make_po)

# python3 make_po.py public_website all
# python3 make_po.py dashboard all
# python3 make_po.py sawaliram_auth all
