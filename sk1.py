from flask import Flask, render_template, request
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import subprocess
import os
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'username'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'example'
mysql = MySQL(app)

@app.route('/')
def index():
    # connect to the database and execute a query
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM form_fields')
    fields = cur.fetchall()
    cur.close()
    
    # generate the HTML form based on the query result
    form = '<h1>Input Form</h1>'
    form += '<form action="/" method="post">'
    for field in fields:
        form += '<label for="{0}">{1}:</label><br>'.format(field[0], field[1])
        if field[2] == 'text':
            form += '<input type="text" id="{0}" name="{0}"><br><br>'.format(field[0])
        elif field[2] == 'email':
            form += '<input type="email" id="{0}" name="{0}"><br><br>'.format(field[0])
        elif field[2] == 'textarea':
            form += '<textarea id="{0}" name="{0}"></textarea><br><br>'.format(field[0])
    form += '<input type="submit" value="Submit">'
    form += '</form>'
    
    return form

@app.route('/', methods=['POST'])
def submit_form():
    # get the form data from the request
    data = {}
    for key in request.form.keys():
        data[key] = request.form[key]
    
    # generate the PDF document
    pdf = canvas.Canvas('form.pdf', pagesize=letter)
    pdf.setFont('Helvetica-Bold', 14)
    for key, value in data.items():
        pdf.drawString(50, 750 - int(key.split('_')[1]) * 50, value)
    pdf.save()
    
    # send the email with the PDF attachment
    subprocess.run(['mailx', '-s', 'Form Submission', '-a', 'form.pdf', 'recipient@example.com'], input='Please see attached PDF file for form submission.')
    
    # delete the PDF file after sending the email
    os.remove('form.pdf')
    
    return 'Form submission successful.'

if __name__ == '__main__':
    app.run()

