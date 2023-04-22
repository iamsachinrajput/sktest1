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



№#######№############


<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Input Form</title>
    <style>
        label {
            display: block;
            margin-bottom: 5px;
        }
        input[type="submit"] {
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Input Form</h1>
    <form method="POST" action="{{ url_for('submit_form') }}">
        {% for field in form_fields %}
            <label>{{ field.name }}</label>
            {% if field.type == 'text' %}
                <input type="text" name="{{ field.field_name }}" required>
            {% elif field.type == 'email' %}
                <input type="email" name="{{ field.field_name }}" required>
            {% elif field.type == 'number' %}
                <input type="number" name="{{ field.field_name }}" required>
            {% elif field.type == 'date' %}
                <input type="date" name="{{ field.field_name }}" required>
            {% endif %}
        {% endfor %}
        <input type="submit" value="Submit">
    </form>
</body>
</html>

############$$$$$$########
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Form Data</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid black;
            padding: 5px;
        }
        th {
            background-color: #ccc;
        }
    </style>
</head>
<body>
    <h1>Form Data</h1>
    <table>
        {% for key, value in form_data.items() %}
            <tr>
                <th>{{ key }}</th>
                <td>{{ value }}</td>
            </tr>
        {% endfor %}
    </table>
</body>
</html>

################

from flask import Flask, render_template, request, make_response
from flask_mysqldb import MySQL
import pdfkit

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'mydatabase'

mysql = MySQL(app)


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM form_fields")
    form_fields = [{'name': row[1], 'field_name': row[2], 'type': row[3]} for row in cur.fetchall()]
    cur.close()
    return render_template('index.html', form_fields=form_fields)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM form_fields")
    form_fields = [{'name': row[1], 'field_name': row[2], 'type': row[3]} for row in cur.fetchall()]
    cur.close()

    form_data = {}
    for field in form_fields:
        form_data[field['name']] = request.form.get(field['field_name'], '')

    # Create PDF using form data and PDF template
    pdf_html = render_template('pdf_template.html', form_data=form_data)
    pdf_file = pdfkit.from_string(pdf_html, False)

    # Email PDF file
    recipient_email = 'recipient@example.com'
    message = f"Here is the form data as a PDF file."
    command = f"echo '{message}' | mailx -s 'Form Data PDF' -a {pdf_file} {recipient_email}"
    import os
    os.system(command)

    return make_response('Form data submitted successfully.')


if __name__ == '__main__':
    app.run(debug=True)

##################


from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'mysecretkey'

# Configure MySQL connection settings
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'mydatabase'

# Create MySQL object
mysql = MySQL(app)


@app.route('/')
def index():
    # Fetch all tables from database
    cursor = mysql.connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]

    return render_template('index.html', tables=tables)


@app.route('/<table_name>')
def table(table_name):
    # Fetch table schema and data
    cursor = mysql.connection.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    columns = [row[0] for row in cursor.fetchall()]

    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()

    return render_template('table.html', table_name=table_name, columns=columns, data=data)


@app.route('/<table_name>/add', methods=['GET', 'POST'])
def add_row(table_name):
    # Fetch column names from table
    cursor = mysql.connection.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    columns = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        # Get form data
        form_data = {}
        for column in columns:
            form_data[column] = request.form.get(column, '')

        # Insert data into table
        cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})", tuple(form_data.values()))
        mysql.connection.commit()

        flash('Row added successfully.')
        return redirect(url_for('table', table_name=table_name))

    return render_template('add_row.html', table_name=table_name, columns=columns)


@app.route('/<table_name>/edit/<int:row_id>', methods=['GET', 'POST'])
def edit_row(table_name, row_id):
    # Fetch column names and data for row with given ID
    cursor = mysql.connection.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    columns = [row[0] for row in cursor.fetchall()]

    cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s", (row_id,))
    row = cursor.fetchone()

    if request.method == 'POST':
        # Get form data
        form_data = {}
        for column in columns:
            form_data[column] = request.form.get(column, '')

        # Update row in table
        set_clause = ', '.join([f"{column} = %s" for column in columns])
        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE id = %s", (*form_data.values(), row_id))
        mysql.connection.commit()

        flash('Row updated successfully.')
        return redirect(url_for('table', table_name=table_name))

    return render_template('edit_row.html', table_name=table_name, columns=columns, row=row)


@app.route('/<table_name>/delete/<int:row_id>')
def delete_row(table_name, row_id):
    # Delete row with given ID from table
    cursor = mysql.connection.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (row_id,))
    mysql.connection.commit()

    flash



#####$##$############
index.html 

<!DOCTYPE html>
<html>
  <head>
    <title>MySQL Tables</title>
  </head>
  <body>
    <h1>MySQL Tables</h1>
    <ul>
      {% for table_name in tables %}
      <li><a href="{{ table_name }}">{{ table_name }}</a></li>
      {% endfor %}
    </ul>
  </body>
</html>


table.html
<!DOCTYPE html>
<html>
  <head>
    <title>{{ table_name }}</title>
  </head>
  <body>
    <h1>{{ table_name }}</h1>
    <table>
      <thead>
        <tr>
          {% for column in columns %}
          <th>{{ column }}</th>
          {% endfor %}
        </tr>
      </thead>
      <tbody>
        {% for row in data %}
        <tr>
          {% for value in row %}
          <td>{{ value }}</td>
          {% endfor %}
          <td><a href="{{ url_for('edit_row', table_name=table_name, row_id=row[0]) }}">Edit</a></td>
          <td><a href="{{ url_for('delete_row', table_name=table_name, row_id=row[0]) }}">Delete</a></td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <a href="{{ url_for('add_row', table_name=table_name) }}">Add row</a>
  </body>
</html>

addrow.html

<!DOCTYPE html>
<html>
  <head>
    <title>Add Row - {{ table_name }}</title>
  </head>
  <body>
    <h1>Add Row - {{ table_name }}</h1>
    <form method="post">
      {% for column in columns %}
      <div>
        <label>{{ column }}</label>
        {% if column == 'date' %}
        <input type="date" name="{{ column }}" required>
        {% elif column == 'integer' %}
        <input type="number" name="{{ column }}" required>
        {% else %}
        <input type="text" name="{{ column }}" required>
        {% endif %}
      </div>
      {% endfor %}
      <button type="submit">Add Row</button>
    </form>
    <a href="{{ url_for('table', table_name=table_name) }}">Cancel</a>
  </body>
</html>

editrow.html

<!DOCTYPE html>
<html>
  <head>
    <title>Edit Row - {{ table_name }}</title>
  </head>
  <body>
    <h1>Edit Row - {{ table_name }}</h1>
    <form method="post">
      {% for column in columns %}
      <div>
        <label>{{ column }}</label>
        {% if column == 'date' %}
        <input type="date" name="{{ column }}" value="{{ row[columns.index(column)+1]|strftime('%Y-%m-%d') }}" required>
        {% elif column == 'integer' %}
        <input type="number" name="{{ column }}" value="{{ row[columns.index(column)+1] }}" required>
        {% else %}
        <input type="text" name="{{ column }}" value="{{ row[columns.index(column)+1] }}" required>
        {% endif %}
      </div>
      {% endfor %}
      <button type="submit">Update Row</button>
    </form>
    <a href="{{ url_for('table', table_name=table_name) }}">Cancel</a>
  </body>
</html



