PROJECT TITLE: NIELSEN ACCIDENT ANALYSIS.
It is advicable to create a github account for ease of code tracking.You can also come up with your own READ.me file for better understanding of your code to other interested profiles.
It is also advicable to listen to music while coding to trick your brain into relaxation.LOL. Preferrably 90s music.

INTRODUCTION AND SETUP.
We will be using Visual Studio Code.
The project begins by creating a folder named NIELSEN_ACCIDENT_ANALYSIS.Inside this folder, create an app.py file and 2 other subfolders namely templates and static. In the templates folder, we will store our html files and in our static  folder we will store our static resources ie pictures and plots and visualization so we can render them in our flask app routes.For this project we will include css and javascript inside our html files.
In visual studio code open the created folder.

The flask web framework will be used alongside Python programming language. The flask framework supports a templating language called Jinga.

WHERE REAL CODING BEGINS.
In our templates folder we will create a base.html file, which will extend to major routes of our flask application via other html templates.Come up with code for your base.html file; include the bootstrap library for responsiveness.It is advicable to generate the  navigation bar and the footer only.This is because when we extend our base.html file to other html templates we require only the general navigation bar and footer to remain the same. We can be able to write code for different body appearance.

we will download the latest version of Python from their website, remember to ADD TO PATH during the setup installation this is VERY CRITICAL.Inside our visual studio code we will select the downloaded python as our interpretor, we will then install the python extension to enhance our coding experience.
In the visual studio code terminal, use pip that comes pre installed with python to install the Flask library, ensure successful installation. Import the Flask library in our app.py file and create a simple flask application.From flask import the render templates library.

All this imports are at the top of the app.py file, it is advicable to always include comments for easy understanding and revision of your code.Render the base.html file inside your flask application to have a look at it, This is crucial in order to view how your base.html file should look like as we will use this file to extend other templates, make sure you are satisfied with the look of your base.html file.

