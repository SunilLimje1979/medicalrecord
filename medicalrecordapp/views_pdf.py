
from medicify_project.models import * 
from medicify_project.serializers import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
import base64
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm, inch

from django.http import HttpResponse
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from reportlab.lib.pagesizes import A4

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table,Image, TableStyle, Preformatted, XPreformatted,HRFlowable,Frame,PageTemplate
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import requests
from datetime import datetime
from translate import Translator
import qrcode
# from PIL import Image
# from PIL import Image as PILImage
margin = 7

pdfmetrics.registerFont(TTFont('Mangal', './Mangal/Mangal.ttf'))
pdfmetrics.registerFont(TTFont('Devanagari', './Mangal/Devanagari.ttf'))

PAGESIZE = A4
BASE_MARGIN = 5 * mm
PAGE_HEIGHT = defaultPageSize[1]; PAGE_WIDTH = defaultPageSize[0]
BottomMargin = 0.4 * inch
TopMargin = 0.4 * inch
LeftMargin = .1 * inch  
RightMargin = .1 * inch
ContentBottomMargin = TopMargin + 0.25 * inch
ContentTopMargin = BottomMargin + 0.35 * inch
ContentLeftMargin = LeftMargin 
ContentRightMargin = RightMargin 


class PdfCreator(APIView):

    def add_page_number(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 10)
        page_number_text = "%d" % (doc.page)
        canvas.drawCentredString(
            0.75 * inch,
            0.75 * inch,
            page_number_text
        )
        canvas.restoreState()

    def get_body_style(self):
        sample_style_sheet = getSampleStyleSheet()
        body_style = sample_style_sheet['BodyText']
        body_style.fontSize = 18
        return body_style

    
    def post(self, request, format=None):
        pdf_buffer = BytesIO()
        my_doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=PAGESIZE,
            topMargin=BASE_MARGIN,
            leftMargin=BASE_MARGIN,
            rightMargin=BASE_MARGIN,
            bottomMargin=BASE_MARGIN
        )
        body_style = self.get_body_style()
        flowables = [
            Paragraph("First paragraph", body_style),
            Paragraph("Second paragraph", body_style)
        ]
        my_doc.build(
            flowables,
            onFirstPage=self.add_page_number,
            onLaterPages=self.add_page_number,
        )
        pdf_value = pdf_buffer.getvalue()
        pdf_buffer.close()

        # Save the PDF to a folder using Django's File Storage
        file_path = default_storage.save('pdfs/your_filename.pdf', ContentFile(pdf_value))
        
        # Get the URL of the saved file
        file_url = default_storage.url(file_path)

        # Return the URL as a response
        return Response({'pdf_url': file_url})
    
@api_view(['POST'])
def fi_generateprescriptionpdf(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    
    doctor_id = request.data.get('doctor_id', None)
    patient_id = request.data.get('patient_id', None)
    doctor_location_id = request.data.get('doctor_location_id', None)
    patient_biometric_id = request.data.get('patient_biometric_id', None)
    Doctor_Location_Availability_Id = request.data.get('Doctor_Location_Availability_Id', None)
    doctor_medicine_id = request.data.get('doctor_medicine_id', None)
    consultation_id = request.data.get('consultation_id', None)
    
    if not doctor_id:
        res = {'message_code': 999, 'message_text': 'Doctor ID is required.'}
    elif not patient_id:
        res = {'message_code': 999, 'message_text': 'Patient id is required.'}
    elif not doctor_location_id:
        res = {'message_code': 999, 'message_text': 'doctor location id is required.'}
    elif not patient_biometric_id:
        res = {'message_code': 999, 'message_text': 'patient biometric id is required.'}
    elif not Doctor_Location_Availability_Id:
        res = {'message_code': 999, 'message_text': 'Doctor location availability id is required.'}
    elif not doctor_medicine_id:
        res = {'message_code': 999, 'message_text': 'Doctor medicine id is required.'}
    elif not consultation_id:
        res = {'message_code': 999, 'message_text': 'consultation id is required.'}
    else:
        try:
            # Fetch doctor data using Django ORM
            url_doctor = 'http://13.233.211.102/doctor/api/get_doctor_by_id/'
            json_data_doctor = {"doctor_id": doctor_id}
            
            response_doctor = requests.post(url_doctor, json=json_data_doctor)

            if response_doctor.status_code == 200:
                json_data_doctor = response_doctor.json()
                result_doctor = json_data_doctor.get('message_data', [])
            else:
                print(f"Error fetching doctor data: {response_doctor.status_code}")
                result_doctor = []

            # Fetch patient data using Django ORM
            url_patient = 'http://13.233.211.102/pateint/api/get_patient_byid/'
            json_data_patient = {"patient_id": patient_id}

            try:
                response_patient = requests.post(url_patient, json=json_data_patient)
                response_patient.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

                json_data_patient = response_patient.json()
                result_patient = json_data_patient.get("message_data", [])
            except requests.exceptions.RequestException as e:
                print(f"Error fetching patient data: {e}")
                result_patient = []

            # Fetch clinick name data using Django ORM
            url_doctor_location = 'http://13.233.211.102/doctor/api/get_all_doctor_location/'
            json_data_doctor_location = {"doctor_location_id": doctor_location_id}

            try:
                response_doctor_location = requests.post(url_doctor_location, json=json_data_doctor_location)
                response_doctor_location.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

                json_data_doctor_location = response_doctor_location.json()
                result_doctor_location = json_data_doctor_location.get("message_data", [])
            except requests.exceptions.RequestException as e:
                print(f"Error fetching patient data: {e}")
                result_doctor_location = []
            
            
            
            # Fetch patientvitals data using Django ORM
            url_patientvitals = 'http://13.233.211.102/medicalrecord/api/get_patientvitals_by_biometric_id/'
            json_data_patientvitals = {"patient_biometric_id":patient_biometric_id}

            try:
                response_patientvitals = requests.post(url_patientvitals, json=json_data_patientvitals)
                response_patientvitals.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

                json_data_patientvitals = response_patientvitals.json()
                result_patientvitals = json_data_patientvitals.get("message_data", [])
            except requests.exceptions.RequestException as e:
                print(f"Error fetching patient data: {e}")
                result_patientvitals = []

            
            # Fetch get_all_doctor_location_availability data using Django ORM
            url_doctor_location_availability = 'http://13.233.211.102/doctor/api/get_all_doctor_location_availability/'
            json_data_doctor_location_availability = {"Doctor_Location_Availability_Id":Doctor_Location_Availability_Id}

            try:
                response_doctor_location_availability = requests.post(url_doctor_location_availability, json=json_data_doctor_location_availability)
                response_doctor_location_availability.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

                json_data_doctor_location_availability= response_doctor_location_availability.json()
                result_doctor_location_availability = json_data_doctor_location_availability.get("message_data", [])
            except requests.exceptions.RequestException as e:
                print(f"Error fetching patient data: {e}")
                result_doctor_location_availability = []
            
            # print(result_doctor_location_availability)
            # Fetch get_all_doctor_medicines data using Django ORM
            url_doctor_doctor_medicines = 'http://13.233.211.102/doctor/api/get_all_doctor_medicines/'
            json_data_doctor_medicines = {"doctor_medicine_id":doctor_medicine_id}

            try:
                response_doctor_medicines = requests.post(url_doctor_doctor_medicines, json=json_data_doctor_medicines)
                response_doctor_medicines.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

                json_data_doctor_medicines= response_doctor_medicines.json()
                result_doctor_medicines = json_data_doctor_medicines.get("message_data", [])
            except requests.exceptions.RequestException as e:
                print(f"Error fetching patient data: {e}")
                result_doctor_medicines = []
            # print(result_doctor_medicines)
                
            # Fetch get_consultation_byconsultationid data using Django ORM
            url_doctor_consultation =  'http://13.233.211.102/medicalrecord/api/get_consultation_byconsultationid/' #'http://localhost:8000/medicalrecord/api/get_consultation_byconsultationid/'
            json_data_consultation = {"consultation_id":consultation_id}

            try:
                response_consultation = requests.post(url_doctor_consultation, json=json_data_consultation)
                response_consultation.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

                json_data_consultation= response_consultation.json()
                result_consultation = json_data_consultation.get("message_data", [])
            except requests.exceptions.RequestException as e:
                print(f"Error fetching patient data: {e}")
                result_consultation = []
            
            if result_doctor and result_patient and result_doctor_location and result_patientvitals and result_doctor_location_availability and result_doctor_medicines and result_consultation:
                # Generate PDF
                pdf_buffer = generate_pdf(result_doctor, result_patient,result_doctor_location,result_patientvitals,result_doctor_location_availability,result_doctor_medicines,result_consultation)
                
                pdf_value = pdf_buffer.getvalue()
                pdf_buffer.close()

                # Save the PDF to a folder using Django's File Storage
                pdfnm = "prescriptionpdfs/" + str(doctor_id) + str(patient_id) + str(patient_biometric_id) + str(doctor_medicine_id) + str(doctor_location_id) + str(Doctor_Location_Availability_Id) + ".pdf"
                file_path = default_storage.save(pdfnm, ContentFile(pdf_value))

                res = {
                    'message_code': 1000,
                    'message_text': "prescription pdf generated successfully.",
                    'message_data':  [{'pdf_url': file_path}],
                    # 'pdf_url': file_path,  # Provide the URL to the saved PDF
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }
            else:
                res = {
                    'message_code': 999,
                    'message_text': "prescription pdf generation failed.",
                    'message_data': [],
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }

        except Exception as e:
            res = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(res)




def generate_pdf(result_doctor,result_patient,result_doctor_location,result_patientvitals,result_doctor_location_availability,result_doctor_medicines,result_consultation):
    pdf_buffer = BytesIO()
    left_margin = 0
    right_margin = 0
    my_doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0, leftMargin=left_margin, rightMargin=right_margin)
    line_break = Spacer(1, 12)
    styles = getSampleStyleSheet()
    center_style = ParagraphStyle(
        'CenterHeading1',
        parent=styles['Heading1'],
        alignment=1,  # 0=left, 1=center, 2=right
    )

    # print(result_doctor)
    first_doctor_data = result_doctor[0]

    # Accessing the value of 'doctor_firstname'
    doctor_firstname = first_doctor_data.get('doctor_firstname',"")
    doctor_lastname = first_doctor_data.get('doctor_lastname',"")
    doctor_registrationno = first_doctor_data.get('doctor_registrationno',"")
    doctor_address =  first_doctor_data.get('doctor_address',"")
    doctor_mobileno =  first_doctor_data.get('doctor_mobileno',"")
    doctor_email =  first_doctor_data.get('doctor_email',"")
    doctor_pincode =  first_doctor_data.get('doctor_pincode',"")
    
    basic_education =  first_doctor_data.get('basic_education',"")
    additional_education =  first_doctor_data.get('additional_education',"")
    services_offered =  first_doctor_data.get('services_offered',"")

    education = basic_education +", "+additional_education
    # print(result_doctor_location)
    # result_doctor_location = result_doctor_location[0]
    # location_title = result_doctor_location('location_title',"")
    location_title = result_doctor_location[0].get('location_title', None)
    heading_text = "<font size=18 color=black><b>"+str(location_title)+"</b></font>"
    heading = Paragraph(heading_text, center_style)
    hr_line = HRFlowable(width="100%", color=colors.black, thickness=2, spaceBefore=10, spaceAfter=10)
    drinfoblock = "<font size=15 color=black><b>" + str(doctor_firstname) + "&nbsp;"+str(doctor_lastname)+"</b></font> "

    print(result_doctor_location_availability)
    availability_day = result_doctor_location_availability.get("availability_day","")
    if availability_day == 1:
        daytime= str(result_doctor_location_availability.get("availability_starttime",""))+"-"+str(result_doctor_location_availability.get("availability_endtime",""))
        
    else:
        daytime=""

    availability_order = result_doctor_location_availability.get("availability_order")

    # Check the value of 'availability_order'
    if availability_order == 1:
        ordertime = "Morning"
    elif availability_order == 2:
        ordertime = "Afternoon"
    elif availability_order == 3:
        ordertime = "Evening"
    else:
        ordertime = ""
    # marathi font
    # hindi_style = ParagraphStyle(
    #     'HindiText',
    #     parent=styles['BodyText'],
    #     fontName='Mangal',  # Use the Mangal font
    #     fontSize=10,
    # )
    hindi_style = ParagraphStyle(
        'HindiText',
        parent=styles['BodyText'],
        fontSize=12,
    )
    services_offered_at = result_doctor_location[0].get('services_offered_at', None)
    print(services_offered_at)
    # Hindi Unicode string
    hindi_text = "नमस्ते, यह एक उदाहरण है!"
    # ,Cardiologist,Dermatologist,Anesthesiologist,Endocrinologist,Family physician
    # marathi font
    table_data = [
        [Paragraph(drinfoblock, styles['BodyText']), Paragraph(services_offered_at, styles['BodyText'])],
        [Paragraph(""+education+"", styles['BodyText'])], 
        #  Paragraph(hindi_text, hindi_style)],
        [Paragraph("Regd. No. "+str(doctor_registrationno)+"", styles['BodyText'])],
        [Paragraph("<font size=10 color=black><b>"+str(services_offered)+"</b></font>", styles['BodyText'])],
        [Paragraph("Time: "+str(ordertime)+" "+str(daytime)+"", styles['BodyText'])],
        [Paragraph(" "+str(doctor_address)+" Pin:"+str(doctor_pincode)+"", styles['BodyText'])],
        
        [Paragraph("Mob. No.:"+str(doctor_mobileno)+"", styles['BodyText'])],
        [Paragraph("E-mail:"+str(doctor_email)+"", styles['BodyText'])],
    ]
    

    table_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.white),
        ('PADDING', (0, 0), (-1, 0), 5),
        ('PADDING', (0, 1), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, 0), 0),
        ('LEFTPADDING', (0, 1), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, 0), 0),
        ('RIGHTPADDING', (0, 1), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
        ('VALIGN', (1, 0), (1, -1), 'TOP'),  # Align second column to the top
        ('SPAN', (1, 0), (1, -1)),
    ])

    # Create the first table
    table = Table(table_data, style=table_style, colWidths=[415, 165])

    # Add content to the PDF
    flowables = [heading, table, hr_line]

    
    first_patient_data = result_patient
    patient_firstname = first_patient_data.get('patient_firstname',"")
    patient_fateherhusbandname = first_patient_data.get('patient_fateherhusbandname',"")
    patient_lastname = first_patient_data.get('patient_lastname',"")
    full_name = str(patient_firstname + " " + patient_fateherhusbandname + " " + patient_lastname)
    
    patient_gender = first_patient_data.get('patient_gender',"")
    if patient_gender==1:
        gender = "Male"
    else:
        gender = "Female"

    patient_mobileno = first_patient_data.get('patient_mobileno',"")
    # Start a new table after the HR line
    Patient = "<font size=10 color=black><b>Patient's Name: "+str(full_name)+"   N/A "+str(gender)+"</b></font>"
    current_date = datetime.now()
    # Format the date
    formatted_date = current_date.strftime(" %b %d, %Y")
    
    current_time = datetime.now().time()
    # Format the time
    formatted_time = current_time.strftime("%I:%M %p")
    Date = "<font size=10 color=black><b>Date: &nbsp;"+str(formatted_date)+",</b></font>"
    Time = "<font size=10 color=black><b>"+str(formatted_time)+"</b></font>"
    hr_line_white = HRFlowable(width="100%", color=colors.white, thickness=2, spaceBefore=10, spaceAfter=10)

    # opd
    
    appointment_id = result_consultation[0].get('appointment_id','')
    if appointment_id:
        formatted_appointment_id = (
            '0' + str(appointment_id) if 1 <= appointment_id <= 9 else str(appointment_id)
        )
    current_month = datetime.now().strftime("%m")
    current_day = datetime.now().strftime("%d")
    opd_appointment_no = str(current_month)+str(current_day)+str(formatted_appointment_id)
    new_table_data = [
        [Paragraph(Patient, styles['BodyText']), Paragraph(Date, styles['BodyText'])],
        
        [Paragraph("Opd No:"+opd_appointment_no+" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  Mob.:"+str(patient_mobileno)+"", styles['BodyText']), Paragraph(Time, styles['BodyText'])],
        # Add more rows as needed
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;DM", styles['BodyText']), Paragraph("", styles['BodyText'])],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;DM", styles['BodyText']), Paragraph("", styles['BodyText'])],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;Hypothyroidism", styles['BodyText']), Paragraph("", styles['BodyText'])],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;COAD", styles['BodyText']), Paragraph("", styles['BodyText'])],

    ]

    table_style_second = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.white),
        ('PADDING', (0, 0), (-1, 0), 5),
        ('PADDING', (0, 1), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, 0), 0),
        ('LEFTPADDING', (0, 1), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, 0), 0),
        ('RIGHTPADDING', (0, 1), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
    ])

    # Create the new table
    new_table = Table(new_table_data, style=table_style_second, colWidths=[415, 165])

    # Add the new table to the PDF
    # flowables.append(new_table,hr_line_white)
    
    flowables.extend([new_table, hr_line_white])

    OE =  "<font size=10 color=black><b>O/E :-</b></font>"
    
    patient_heartratepluse = result_patientvitals[0].get('patient_heartratepluse', None)
    patient_bpsystolic = result_patientvitals[0].get('patient_bpsystolic', None)
    patient_bpdistolic = result_patientvitals[0].get('patient_bpdistolic', None)
    patient_painscale = result_patientvitals[0].get('patient_painscale', None)
    patient_respiratoryrate = result_patientvitals[0].get('patient_respiratoryrate', None)
    patient_temparature = result_patientvitals[0].get('patient_temparature', None)
    patient_chest = result_patientvitals[0].get('patient_chest', None)
    patient_ecg = result_patientvitals[0].get('patient_ecg', None)
    bp = str(patient_bpsystolic) +"/"+str(patient_bpdistolic)

    medicine_name = result_doctor_medicines[0].get('medicine_name', None)
    medicine_duration = result_doctor_medicines[0].get('medicine_duration', None)
    medicine_dosages = result_doctor_medicines[0].get('medicine_dosages', None)
    result_doctor_medicines_rx = "<font size=10 color=black><b>RX :- </b></font>"
    result_doctor_medicines_name = "<font size=10 color=black><b>"+str(medicine_name)+" </b></font>"
    result_doctor_medicines_duration = "<font size=10 color=black><b>"+str(medicine_duration)+" </b></font>"
    result_doctor_medicines_dosages = "<font size=10 color=black><b>"+str(medicine_dosages)+" </b></font>"
    
    new_table_data_three = [
        [Paragraph("Wt&nbsp;:&nbsp;&nbsp;&nbsp;80 Kg", styles['BodyText']), Paragraph(OE, styles['BodyText']), Paragraph(result_doctor_medicines_rx, styles['BodyText'])],
        [Paragraph("Ht&nbsp;:&nbsp;&nbsp;&nbsp; 185 Cm", styles['BodyText']), Paragraph("Pulse &nbsp;:&nbsp;&nbsp;&nbsp; "+str(patient_heartratepluse)+"/min" , styles['BodyText']), Paragraph(result_doctor_medicines_name, styles['BodyText'])],
        [Paragraph("Hr&nbsp;:&nbsp;&nbsp;&nbsp;70", styles['BodyText']), Paragraph("Temp&nbsp;:&nbsp;&nbsp;&nbsp; "+str(patient_temparature)+"", styles['BodyText']), Paragraph(result_doctor_medicines_dosages, styles['BodyText'])],
        [Paragraph("Bp&nbsp;:&nbsp;&nbsp;&nbsp;"+str(bp)+"", styles['BodyText']), Paragraph("Pallor &nbsp;:&nbsp;&nbsp;&nbsp; 2", styles['BodyText']), Paragraph(result_doctor_medicines_duration, styles['BodyText'])],
       
       [Paragraph("", styles['BodyText']), Paragraph("Oedema Feet &nbsp;:&nbsp;&nbsp;&nbsp; 2", styles['BodyText']), Paragraph("", styles['BodyText'])],
       [Paragraph("", styles['BodyText']), Paragraph("GC &nbsp;:&nbsp;&nbsp;&nbsp; 5", styles['BodyText']), Paragraph("", styles['BodyText'])],
       [Paragraph("", styles['BodyText']), Paragraph("RS &nbsp;:&nbsp;&nbsp;&nbsp; Wnl", styles['BodyText']), Paragraph("", styles['BodyText'])],
       [Paragraph("", styles['BodyText']), Paragraph("RS Other &nbsp;:&nbsp;&nbsp;&nbsp; RS 0323", styles['BodyText']), Paragraph("", styles['BodyText'])],
       [Paragraph("", styles['BodyText']), Paragraph("PA &nbsp;:&nbsp;&nbsp;&nbsp; Soft", styles['BodyText']), Paragraph("", styles['BodyText'])],
       [Paragraph("", styles['BodyText']), Paragraph("PA Other &nbsp;:&nbsp;&nbsp;&nbsp; PA 0323", styles['BodyText']), Paragraph("", styles['BodyText'])],
       
    ]

    new_table_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.white),
        ('PADDING', (0, 0), (-1, 0), 0),
        ('PADDING', (0, 1), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, 0), 0),
        ('LEFTPADDING', (0, 1), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, 0), 0),
        ('RIGHTPADDING', (0, 1), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, 0), 0),
        ('TOPPADDING', (0, 1), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 0)
    ])

    # Create the new table
    new_table_three = Table(new_table_data_three, style=new_table_style, colWidths=[193, 193, 193])

    # Add the new table to the PDF
    # flowables.append(new_table_three,hr_line_white)
    flowables.extend([new_table_three, hr_line_white])
    # third section end

    # fourth section start
    Advice =  "<font size=10 color=black><b>Advice :-</b></font>"

    new_table_data_four = [
        [Paragraph(Advice, styles['BodyText']), Paragraph("Hospitalization", styles['BodyText'])],
        [Paragraph("C.T. Scan", styles['BodyText']), Paragraph("Review after 4 Days on Mar 28, 2023" , styles['BodyText'])],
        [Paragraph("Paracheck for MPÐ", styles['BodyText']), Paragraph("" , styles['BodyText'])],
        [Paragraph("CBC", styles['BodyText']), Paragraph("" , styles['BodyText'])],
        
       
    ]

    new_table_style_four = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.white),
        ('PADDING', (0, 0), (-1, 0), 0),
        ('PADDING', (0, 1), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, 0), 0),
        ('LEFTPADDING', (0, 1), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, 0), 0),
        ('RIGHTPADDING', (0, 1), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, 0), 0),
        ('TOPPADDING', (0, 1), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 0)
    ])

    # Create the new table
    new_table_four = Table(new_table_data_four, style=new_table_style_four, colWidths=[290,290])

    # Add the new table to the PDF
    # flowables.append(new_table_four,hr_line_white)
    flowables.extend([new_table_four, hr_line_white])
    #fourth section end







    my_doc.build(flowables)
    return pdf_buffer

##################################################################clinic pdf
    
@api_view(['POST'])
def fi_generateclinicpdf(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    
    doctor_id = request.data.get('doctor_id', None)
    # patient_id = request.data.get('patient_id', None)
    doctor_location_id = request.data.get('doctor_location_id', None)
    # patient_biometric_id = request.data.get('patient_biometric_id', None)
    Doctor_Location_Availability_Id = request.data.get('Doctor_Location_Availability_Id', None)
    
    
    if not doctor_id:
        res = {'message_code': 999, 'message_text': 'Doctor ID is required.'}
    # elif not patient_id:
    #     res = {'message_code': 999, 'message_text': 'Patient id is required.'}
    elif not doctor_location_id:
        res = {'message_code': 999, 'message_text': 'doctor location id is required.'}
    # elif not patient_biometric_id:
    #     res = {'message_code': 999, 'message_text': 'patient biometric id is required.'}
    elif not Doctor_Location_Availability_Id:
        res = {'message_code': 999, 'message_text': 'Doctor location availability id is required.'}
    else:
        try:
            # Fetch doctor data using Django ORM
            url_doctor = 'http://13.233.211.102/doctor/api/get_doctor_by_id/'
            json_data_doctor = {"doctor_id": doctor_id}
            
            response_doctor = requests.post(url_doctor, json=json_data_doctor)

            if response_doctor.status_code == 200:
                json_data_doctor = response_doctor.json()
                result_doctor = json_data_doctor.get('message_data', [])
            else:
                print(f"Error fetching doctor data: {response_doctor.status_code}")
                result_doctor = []
            
            # Fetch clinick name data using Django ORM
            url_doctor_location = 'http://13.233.211.102/doctor/api/get_all_doctor_location/'
            json_data_doctor_location = {"doctor_location_id": doctor_location_id}

            try:
                response_doctor_location = requests.post(url_doctor_location, json=json_data_doctor_location)
                response_doctor_location.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

                json_data_doctor_location = response_doctor_location.json()
                result_doctor_location = json_data_doctor_location.get("message_data", [])
            except requests.exceptions.RequestException as e:
                print(f"Error fetching patient data: {e}")
                result_doctor_location = []
            
            
            # Fetch get_all_doctor_location_availability data using Django ORM
            url_doctor_location_availability = 'http://13.233.211.102/doctor/api/get_all_doctor_location_availability/'
            json_data_doctor_location_availability = {"Doctor_Location_Availability_Id":Doctor_Location_Availability_Id}

            try:
                response_doctor_location_availability = requests.post(url_doctor_location_availability, json=json_data_doctor_location_availability)
                response_doctor_location_availability.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

                json_data_doctor_location_availability= response_doctor_location_availability.json()
                result_doctor_location_availability = json_data_doctor_location_availability.get("message_data", [])
            except requests.exceptions.RequestException as e:
                print(f"Error fetching patient data: {e}")
                result_doctor_location_availability = []
            
            if result_doctor and result_doctor_location and result_doctor_location_availability:
            # and result_patient and result_doctor_location and result_patientvitals and result_doctor_location_availability:
                # Generate PDF
                pdf_buffer = generate_clinic_pdf(result_doctor_location,result_doctor,result_doctor_location_availability)
                # , result_patient,result_doctor_location,result_patientvitals,result_doctor_location_availability)
                
                pdf_value = pdf_buffer.getvalue()
                pdf_buffer.close()

                # Save the PDF to a folder using Django's File Storage
                pdfnm = "clinicpdfs/" + str(doctor_id) + str(doctor_location_id) + str(Doctor_Location_Availability_Id) + ".pdf"
                file_path = default_storage.save(pdfnm, ContentFile(pdf_value))

                res = {
                    'message_code': 1000,
                    'message_text': "clinic pdf generated successfully.",
                    'message_data':  [{'pdf_url': file_path}],
                    # 'pdf_url': file_path,  # Provide the URL to the saved PDF
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }
            else:
                res = {
                    'message_code': 999,
                    'message_text': "clinic pdf generation failed.",
                    'message_data': [],
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }

        except Exception as e:
            res = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(res)


def add_border(canvas, doc):
    print("Adding border to page...")
    canvas.saveState()
    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(0.2)
    width, height = A4
    margin = 10  # Adjust the margin as needed
    border_width = 0.2
    canvas.line(margin - border_width, margin - border_width, margin - border_width, height - margin + border_width)  # Left border
    canvas.line(margin - border_width, height - margin + border_width, width - margin + border_width, height - margin + border_width)  # Bottom border
    canvas.line(width - margin + border_width, height - margin + border_width, width - margin + border_width, margin - border_width)  # Right border
    canvas.line(width - margin + border_width, margin - border_width, margin - border_width, margin - border_width)  # Top border
    canvas.restoreState()


def translate_to_marathi(text):
    translator= Translator(to_lang="mr")  # "mr" is the language code for Marathi
    translation = translator.translate(text)
    return translation

def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")

    qr_code_bytes = BytesIO()
    qr_image.save(qr_code_bytes, format='PNG')
    
    return qr_code_bytes

def generate_clinic_pdf(result_doctor_location,result_doctor,result_doctor_location_availability):
    pdf_buffer = BytesIO()
    left_margin = 10
    right_margin = 10
    A4 = (595.276, 841.890)
    
    # Calculate frame dimensions
    frame_width = A4[0] - left_margin - right_margin
    frame_height = A4[1] - 2 * margin  # Adjusted to account for top and bottom margins
    my_doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0, leftMargin=left_margin, rightMargin=right_margin)
    # Add a custom page template with borders
    my_doc.addPageTemplates([PageTemplate(id='border_template', frames=[Frame(left_margin, margin, frame_width, frame_height, showBoundary=0)], onPage=add_border)])
    styles = getSampleStyleSheet()
    hindi_style = ParagraphStyle(
        'HindiText',
        parent=styles['BodyText'],
        fontName='Mangal',  # Use the Mangal font
        fontSize=25,
    )

    # Hindi Unicode string
    hindi_text = "नमस्ते, यह एक उदाहरण है!"
    img_path = 'img/logo1.jpg'
    # content_text = "Shree Clinic"
    
    location_title = result_doctor_location[0].get('location_title', None)
    content_text = "<font size=18 color=black><b>"+str(location_title)+"</b></font>"
    marathi_translation = translate_to_marathi(content_text)

    
    first_doctor_data = result_doctor[0]

    # Accessing the value of 'doctor_firstname'
    doctor_firstname = first_doctor_data.get('doctor_firstname',"")
    doctor_lastname = first_doctor_data.get('doctor_lastname',"")
    doctor_registrationno = first_doctor_data.get('doctor_registrationno',"")
    doctor_address =  first_doctor_data.get('doctor_address',"")
    doctor_firstname_marathi = translate_to_marathi(doctor_firstname)
    doctor_lastname_marathi = translate_to_marathi(doctor_lastname)
    doctor_address_marathi = translate_to_marathi(doctor_address)
    hindi_style_address = ParagraphStyle(
        'HindiText',
        parent=styles['BodyText'],
        fontName='Mangal',  # Use the Mangal font
        fontSize=15,
    )
    
    content_style_eng = ParagraphStyle(name='Content', fontSize=15)
    # # Create styles
    styles = getSampleStyleSheet()
    content_style = ParagraphStyle(name='Content', fontSize=25, leading=14,topMargin=0)
    # Create image
    img = Image(img_path, width=100, height=100)
    
    # Create a table to arrange image and content
    data = [[img,Paragraph(content_text, content_style), Paragraph(marathi_translation, hindi_style)],
             [Paragraph("", content_style), Paragraph(doctor_address, content_style_eng),Paragraph(doctor_address_marathi, hindi_style_address)],
            ]
        # [img, content_paragraph]]
    table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'LEFT'),  # Vertical alignment in the middle
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),  # Alignment of the content to the left
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),  # Bottom padding  # Add grid lines
    ])
    table = Table(data, style=table_style)
    # Add content to the PDF
    flowables = [table]

    drtimefont = ParagraphStyle(
        'HindiText',
        parent=styles['BodyText'],
        fontName='Mangal',  # Use the Mangal font
        fontSize=15,
    )
    drfullnmeng = str(doctor_firstname)+" "+str(doctor_lastname)
    drfullnmmarathi = str(doctor_firstname_marathi)+" "+str(doctor_lastname_marathi)
    
    # drname="डॉ.संदीप मोहिते"
    # drname2="डॉ.भाग्यश्री मोहिते"
    opdtimingmarathi = "दवाखान्यांची वेळ"
    content_style_time = ParagraphStyle(name='Content', fontSize=15, leading=14)
    availability_day = result_doctor_location_availability.get("availability_day","")
    if availability_day == 1:
        daytime= str(result_doctor_location_availability.get("availability_starttime",""))+"-"+str(result_doctor_location_availability.get("availability_endtime",""))
        
    else:
        daytime=""

    availability_order = result_doctor_location_availability.get("availability_order")

    # Check the value of 'availability_order'
    if availability_order == 1:
        ordertime = "Morning"
    elif availability_order == 2:
        ordertime = "Afternoon"
    elif availability_order == 3:
        ordertime = "Evening"
    else:
        ordertime = ""
    timemeng = str(ordertime)+" "+str(daytime)
    timemarathi=translate_to_marathi(timemeng)

    table_data = [
        [ Paragraph(drfullnmmarathi, hindi_style),Paragraph(drfullnmeng, content_style)],
        # [ Paragraph(drname2, hindi_style),Paragraph("Dr.Bhagyashree Mohite", content_style)],
        [ Paragraph(opdtimingmarathi, drtimefont),Paragraph("OPD Timing", content_style_time)],
        [ Paragraph(timemeng, content_style_time),Paragraph(timemarathi, hindi_style_address)],
    ]
    table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'LEFT'),  # Vertical alignment in the middle
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),  # Alignment of the content to the left
        ('GRID', (0, 0), (-1, -1), 1, colors.gray),
        ('BACKGROUND', (0, 0), (-1, -1), colors.gray),  # Add grid lines
        ('LEFTPADDING', (0, 0), (-1, -1), 10),  # Left padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),  # Right padding
        ('TOPPADDING', (0, 0), (-1, -1), 3),  # Top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),  # Bottom padding
    ])

    # Create the first table
    table = Table(table_data, style=table_style, colWidths=[288, 288])
    flowables.extend([table])

    center_style = ParagraphStyle(
        'CenterHeading1',
        parent=styles['Heading1'],
        alignment=1,  # 0=left, 1=center, 2=right
    )
    hindi_style3 = ParagraphStyle(
        'HindiText',
        parent=styles['BodyText'],
        fontName='Mangal',  # Use the Mangal font
        fontSize=15,
         alignment=1, 
    )
    # book appotment
    notehindi = "कृपया बुक अपॉईटमेंटसाठी हा क्यूआर कोड स्कॅन करा"
    noteenglish = "Please scan this QR code to book appoitment"
    # marathi font
    table_data = [
        [ Paragraph(notehindi, hindi_style3)],
        [ Paragraph(noteenglish, center_style)],
    ]
    table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'LEFT'),  # Vertical alignment in the middle
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Alignment of the content to the left
        ('GRID', (0, 0), (-1, -1), 1, colors.white),  # Add grid lines
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),  # Left margin
    ])
    table = Table(table_data, style=table_style, colWidths=[500])
    flowables.extend([table])
    #qr
    location_qr_url = result_doctor_location[0].get('location_qr_url', None)
    url = location_qr_url
    styles = getSampleStyleSheet()
    qr_code_image = generate_qr_code(url)
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    img = Image(qr_code_image, width=400, height=400)
    flowables.extend([img])  # Wrap the image object in a list and extend

    # 
    abhari = "आभारी आहोत!"
    thank = "Thank You!"
    table_data = [
        [ Paragraph(abhari, hindi_style3),Paragraph(thank, center_style)],
    ]
    table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'LEFT'),  # Vertical alignment in the middle
        ('ALIGN', (0, 0), (0, 0), 'CENTER'), # Alignment of the content to the left
        ('GRID', (0, 0), (-1, -1), 1, colors.white),  # Add grid lines
    ])
    table = Table(table_data, style=table_style, colWidths=[150,150])
    flowables.extend([table])
    medilineapp = "this facility powered by av mediline app"
    table_data = [
        [ Paragraph(medilineapp, center_style)],
    ]
    table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'LEFT'),  # Vertical alignment in the middle
        ('ALIGN', (0, 0), (0, 0), 'CENTER'), # Alignment of the content to the left
        ('GRID', (0, 0), (-1, -1), 1, colors.white),  # Add grid lines
    ])
    table = Table(table_data, style=table_style, colWidths=[500])
    flowables.extend([table])

    my_doc.build(flowables)
    return pdf_buffer

