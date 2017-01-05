 FROM registry.tjoomla.com:5000/mezzaninedocker_web:v4
# FROM kakadadroid/python-talib

 ENV PYTHONUNBUFFERED 1
 RUN mkdir -p /code
 WORKDIR /code
 ADD requirements.txt /code/
 RUN pip install -r requirements.txt
 RUN pip install https://github.com/mrjbq7/ta-lib/archive/TA_Lib-0.4.8.zip
 ADD . /code/

# RUN python manage.py makemigrations --noinput
# RUN python manage.py migrate --noinput
 RUN python manage.py collectstatic --noinput