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






##############$


from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import pdfkit
import subprocess

app = Flask(__name__)
app.secret_key = 'secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'username'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'database_name'
mysql = MySQL(app)

# Route for the input form
@app.route('/', methods=['GET', 'POST'])
def input_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        comments = request.form['comments']
        phone_number = request.form['phone_number']
        date_of_birth = request.form['date_of_birth']
        age = request.form['age']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO form_data(name, email, comments, phone_number, date_of_birth, age) VALUES (%s, %s, %s, %s, %s, %s)", (name, email, comments, phone_number, date_of_birth, age))
        mysql.connection.commit()
        cur.close()
        flash('Form data has been saved successfully!', 'success')
        return redirect(url_for('input_form'))
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM form_fields")
        fields = cur.fetchall()
        cur.close()
        return render_template('index.html', fields=fields)

# Route for generating the PDF file and sending it as an email
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    comments = request.form['comments']
    phone_number = request.form['phone_number']
    date_of_birth = request.form['date_of_birth']
    age = request.form['age']
    form_data = {
        'Name': name,
        'Email': email,
        'Comments': comments,
        'Phone Number': phone_number,
        'Date of Birth': date_of_birth,
        'Age': age
    }
    html = render_template('pdf_template.html', form_data=form_data)
    pdf_file = 'form_data.pdf'
    pdfkit.from_string(html, pdf_file)
    command = 'echo "Please find attached the form data" | mailx -s "Form Data" -a "{}" {}'.format(pdf_file, email)
    subprocess.call(command, shell=True)
    flash('Form data has been saved and emailed successfully!', 'success')
    return redirect(url_for('input_form'))

if __name__ == '__main__':
    app.run(debug=True)
