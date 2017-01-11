 FROM registry.tjoomla.com:5000/mezzaninedocker_web:v4
# FROM kakadadroid/python-talib
 RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 627220E7
 RUN echo 'deb http://archive.scrapy.org/ubuntu scrapy main' > /etc/apt/sources.list.d/scrapy.list
 RUN apt-get autoclean
 RUN apt-get update -y && apt-get upgrade -y && apt-get install -y procenv scrapyd
 RUN pip install --upgrade six
 RUN pip install scrapyd-client
 ENV PYTHONUNBUFFERED 1
 RUN mkdir -p /code
 WORKDIR /code
 ADD requirements.txt /code/
 RUN pip install pip -U
 RUN pip install -r requirements.txt
# RUN pip install https://github.com/mrjbq7/ta-lib/archive/TA_Lib-0.4.8.zip
 ADD . /code/

 EXPOSE 8000
 EXPOSE 6800

# RUN python manage.py makemigrations --noinput
# RUN python manage.py migrate --noinput
 RUN python manage.py collectstatic --noinput