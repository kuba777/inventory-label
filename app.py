from flask import Flask, render_template, request, Response, send_file
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
from reportlab.lib import utils
from reportlab.platypus import Frame, Image
from datetime import datetime, date

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import csv

BINS = "bin_location.txt"  # tab separated file
LOGO = "logo.png"

app = Flask(__name__)


def read_bin_file():

    bin_array = []

    with open(BINS) as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        next(tsvreader)
        for line in tsvreader:

            item = line[0]
            # bin_id = line[1]
            try:
                bin_id = line[1]
            except IndexError:
                # print("index error", item)
                bin_id = " "
                
            bin_array.append([item, bin_id])

    return bin_array


@app.route('/label')
def index():
    bin_array = read_bin_file()
          
    today = date.today()
    
    return render_template('label.html', bin_array=bin_array, today=today)


@app.route('/generate-label', methods=['GET', 'POST'])
def generate_label():
    label_dict = {}
    if request.method == 'POST':
        # Retrieve user input from the form
        part_number = request.form.get('part_number')
        revision = request.form.get('revision')
        qty = request.form.get('qty')
        date_open = request.form.get('date_open')
        lot = request.form.get('lot')
        location = request.form.get('location')
         
        # Validate and store the user input
        if part_number and revision: # and publication_year:
            label_dict = {
                'part_number': part_number,
                'revision': revision,
                'qty': qty,
                'date_open': date_open,
                'lot': lot,
                'location': location
            }
            
    pdf_file = generate_pdf_file(label_dict)
    return send_file(pdf_file, as_attachment=False, download_name='label.pdf')


def generate_pdf_file(label_dict):

    logo = ImageReader(LOGO)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 9)

    w, h = 4 * inch, 2.31  * inch
    pagesize = (w, h)
    p.setPageSize(pagesize)

    # print("p.pagesize", dir(p.pagesize()))
    
    # Create a PDF document
    p.drawImage(logo, w * 0.09, h - 0.55*inch, 1.28*inch, 0.44*inch, mask='auto')

    p.setFont("Helvetica-Bold", 10)
    p.drawString(w * 0.46, h - 0.45*inch, "Inventory Ticket")

    p.setFont("Helvetica", 5)
    p.drawString(w * 0.8, h - 0.35*inch, "QF15-04.  Rev 1.")

    p.setFont("Helvetica", 9)
    # textobject.setFont(psfontname, size, leading = None)


    p.setLineWidth(0.5)
    story = []
    frame = Frame(.25*inch, .25*inch, w - .5*inch, 1.50*inch, showBoundary=1)
    frame.addFromList(story, p)

    # canvas.line(x1,y1,x2,y2)
    # horizontal
    p.line(.25*inch, 1.30*inch, w - .25*inch, 1.30*inch)
    p.line(.25*inch, .80*inch, w - .25*inch, .80*inch)

    # vertical
    p.line(1.33*inch, .80*inch, 1.33*inch, 1.30*inch)
    p.line(2.53*inch, .80*inch, 2.53*inch, 1.75*inch)


    # Labels, first column
    y = h - 0.7*inch
    p.drawString(w * 0.09, y, f"Part number")
    p.drawString(w * 0.09, y - 35, f"Quantity")
    p.drawString(w * 0.09, y - 70, f"Location")

    # second column
    p.drawString(w * 0.35, y - 35, f"Date Open")

    # third column
    p.drawString(w * 0.65, y, f"Revision")
    p.drawString(w * 0.65, y - 35, f"Lot")


    # data fields
    # p.drawString(w * 0.09, y, f"Part number {book['part_number']}")


    qty = label_dict['qty']
    qty = '{:,}'.format(int(qty)).replace(',', ' ')
    a = 17 # first column
    # b =
    p.setFont("Helvetica", 12)
    # for label_dict in user_data:
    p.drawString(w * 0.09,  y - a , f"{label_dict['part_number'] : >23}")
    p.drawString(w * 0.09,  y - 34 - a, f"{qty : >10}")
    p.drawString(w * 0.09,  y - 70 - a, f"{label_dict['location'] : >35}")

    # second column
    datetime_object = datetime.strptime(label_dict['date_open'],'%Y-%m-%d')
    date = f"{datetime_object:%d-%b-%Y}"
    p.drawString(w * 0.36, y - 34 - a, f"{date : >10}")


    # third column
    p.drawString(w * 0.65, y - a, f"{label_dict['revision'] : >12}")
    p.drawString(w * 0.65, y - 35 - a, f"{label_dict['lot'] : >12}")




    p.showPage()
    p.save()
 
    buffer.seek(0)
    return buffer


if __name__ == '__main__':
    app.run(debug=True)

    # label info:
    
    # label page: width 4'', height 2.31''
    # 2 5/16 x 4 ''
    # landscape
