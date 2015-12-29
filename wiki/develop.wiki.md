##Develop With Us

Download the latest version of Doc-docs. It's not required that you have Vagrant installed but it is highly recommended 
so that we can be certain to develop in the same environment as the live application. If you choose to develop without 
using Vagrant and run into issues, please install Vagrant before asking questions on the forums.


###Up and Running, compiling, serving, watching...
Docdocs runs over the Python Flask framework, as a web developer I know how important it is to have great tools such 
as SASS and Live Reload. You aren't required to use these tools unless 
you're working on the css for the Doc-docs page. So To make things simple, I decided to use Nodejs and Gulp to handle 
compilations from .scss to .csss as well as live reload in the development environment. Once you have your development 
environment running `cd /vagrant/doc-docs` then run `gulp && ipython run.py` to serve the application to your 
localhost port 5000 and gulp will compile your .scss and reload the webpage in browser.