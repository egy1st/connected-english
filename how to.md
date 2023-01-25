# How to run virtual enviroment

cd C:\Users\moham\Documents\GitHub\connected-english

python3 -m venv venv
//or//
py -3 -m venv venv

venv\Scripts\activate


# How to run flask
flask run


# How to heroku

 - heroku login
 - first time only|| git checkout -b main  // change branch to main
 - first time only|| git add .  // add all
 - then ||  git add -A  // add only changes
 -  git commit -am "make it better"
 -  git push heroku main

 - set local to heroku project (first time only) || heroku git:remote -a connected-english
 - clone from herku to local (then if needed) || heroku git:clone -a connected-english 


# load corpora for nltk
Add a nltk.txt file to your root directory and list your corpora inside





Github KB
=========

…or create a new repository on the command line
echo "# connected-english" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/egy1st/connected-english.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin https://github.com/egy1st/connected-english.git
git branch -M main
git push -u origin main

…or push an existing repository from the command line
git remote add origin https://github.com/egy1st/connected-english.git
git branch -M main
git push -u origin main