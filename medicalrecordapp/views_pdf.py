import os
from django.db import connection
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

from reportlab.lib.pagesizes import A4 ,landscape

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
import pytz

from django.db.models import Q

from medicalrecord import settings
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

        file_path = default_storage.save('pdfs/your_filename.pdf', ContentFile(pdf_value))
        file_url = default_storage.url(file_path)
        return Response({'pdf_url': file_url})
    
@api_view(['POST'])
def fi_generateprescriptionpdf(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    
    consultation_id = request.data.get('consultation_id', None)
    
    if not consultation_id:
        res = {'message_code': 999, 'message_text': 'consultation id is required.'}
    
    else:
        try:
            
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
            
            if result_consultation:
                doctor_id = result_consultation[0].get('doctor_id','')
            else:
                doctor_id =""
            # Fetch doctor data using Django ORM
            if doctor_id:
                url_doctor = 'http://13.233.211.102/doctor/api/get_doctor_by_id/'
                json_data_doctor = {"doctor_id": doctor_id}
                
                response_doctor = requests.post(url_doctor, json=json_data_doctor)

                if response_doctor.status_code == 200:
                    json_data_doctor = response_doctor.json()
                    result_doctor = json_data_doctor.get('message_data', [])
                else:
                    print(f"Error fetching doctor data: {response_doctor.status_code}")
                    result_doctor = []
            else:
                result_doctor = []

            if result_consultation:
                patient_id = result_consultation[0].get('patient_id','')
            else:
                patient_id =""
            
            if patient_id:
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
            else:
                result_patient = []
            
            if doctor_id:
                doctor_location = Tbldoctorlocations.objects.filter(
                    Q(doctor_id=doctor_id,isdeleted=0)
                ).order_by('doctor_location_id').first()

                serializer = DoctorLocationSerializer(doctor_location)
                result = serializer.data
                if result:
                    result_doctor_location = result
                else:
                    result_doctor_location = []
            else:
                result_doctor_location = []

            if consultation_id and doctor_id and patient_id:
                patientvital = Tblpatientvitals.objects.filter(consultation_id=consultation_id,doctor_id=doctor_id,patient_id=patient_id).order_by('patient_biometricid').first()
                serializer = TblPatientVitalsSerializer(patientvital)
                result = serializer.data
                result_patientvitals = result
            else:
                result_patientvitals = []
            

            if result_doctor_location:
                doctor_location_id_int = result_doctor_location['doctor_location_id']
            else:
                doctor_location_id_int = ""
            if doctor_location_id_int and doctor_id:
                instance = Tbldoctorlocationavailability.objects.filter(doctor_location_id=doctor_location_id_int, doctor_id=doctor_id, isdeleted=0).order_by('doctor_location_availability_id').first()
                if instance:
                    serializer = DoctorLocationAvailabilitySerializer(instance)
                    result_doctor_location_availability = serializer.data
                else:
                    result_doctor_location_availability = []
            else:
                result_doctor_location_availability = []

            if consultation_id and doctor_id and patient_id:
                patient_medications = TblpatientMedications.objects.filter(consultation_id=consultation_id, doctor_id=doctor_id, patient_id=patient_id,isdeleted=0)
                serializer = MedicationsSerializer(patient_medications, many=True)
                result_patient_medications = serializer.data

                # Fetching instruction text
                for medication_record in result_patient_medications:
                    medicine_instruction_id = medication_record.get('medicine_instruction_id')
                    if medicine_instruction_id:
                        medicineInstruction = TblmedicineInstructions.objects.get(doctor_instruction_id=medicine_instruction_id)
                        serializer_medicine_inst = TblmedicineInstructionsSerializer(medicineInstruction)
                        # print(serializer_medicine_inst.data)
                        instruction_text = serializer_medicine_inst.data.get('instruction_text', "")
                        medication_record['doctor_instruction_text'] = instruction_text
                
                findings_symptoms = TblpatientFindingsandsymtoms.objects.filter(consultation_id=consultation_id)
                serializer = TblpatientFindingsandsymtomsSerializer(findings_symptoms, many=True)
                result_findings_symptoms=serializer.data
                # print(result_findings_symptoms)
            else:
                result_patient_medications = []
                result_findings_symptoms=[]
                # instruction end

            if result_consultation:
                # Generate PDF
                pdf_buffer = generate_pdf(result_doctor, result_patient,result_doctor_location,result_patientvitals,result_doctor_location_availability,result_patient_medications,result_consultation,result_findings_symptoms)
                
                pdf_value = pdf_buffer.getvalue()
                pdf_buffer.close()
                
                pdf_filename = f"{doctor_id}{patient_id}{consultation_id}.pdf"

                pdf_path = os.path.join(settings.PDF_ROOT2, pdf_filename)
                # file_path = default_storage.save(pdf_path, ContentFile(pdf_value))
                # absolute_file_path = default_storage.path(file_path)
                # url_path = default_storage.url(file_path)
                # absolute_file_path = absolute_file_path.replace('\\', '/')
                # url_path = url_path.replace('\\', '/')
                # normalized_path = os.path.normpath(absolute_file_path)
                # final_path = str(normalized_path)
                file_path = default_storage.save(pdf_path, ContentFile(pdf_value))
                absolute_file_path = default_storage.path(file_path)

                # Convert the path to a string without hyperlink
                final_path = str(absolute_file_path.replace('\\', '/'))
                url_prefix = "http://13.233.211.102/medicalrecord/static/"
                url = final_path.replace("/home/ubuntu/medicalrecord/staticfiles/", url_prefix)
                res = {
                    'message_code': 1000,
                    'message_text': "prescription pdf generated successfully.",
                    'message_data':  [{'pdf_url': url}],
                   'message_debug': [{"Debug": debug}] if debug != "" else []
                }
            else:
                res = {
                    'message_code': 999,
                    'message_text': "prescription pdf generation failed, consultation_id not found.",
                    'message_data': [],
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }

        except Exception as e:
            res = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(res)




def generate_pdf(result_doctor,result_patient,result_doctor_location,result_patientvitals,result_doctor_location_availability,result_patient_medications,result_consultation,result_findings_symptoms):
    print(result_doctor)
    detail_url="http://13.233.211.102/doctor/api/get_prescription_settings_by_doctor/"
    detail_response=requests.post(detail_url,json={'doctor_id':result_doctor[0].get('doctor_id')})
    print(detail_response.text)
    pagesize = A4
    if(detail_response.json().get('message_code')==1000):
            prescription_settings=(detail_response.json()).get('message_data')
            print(prescription_settings)
            if prescription_settings['paper_size'] == 2:
                pagesize = landscape((A4[0], A4[1] / 2))
            if(prescription_settings['header_type']==2):
                link=prescription_settings['header_image']
                # link=None
                if(link is not None):
                    # Replace '/staticfiles/' with '/static/'
                    updated_link = link.replace('/staticfiles/', '/static/')
                    img_path="http://13.233.211.102/doctor"+updated_link
                    header_top_margin_in_inches = (float(prescription_settings['header_top_margin']) if prescription_settings['header_top_margin'] else 0)
                    header_top_margin_in_pixels = header_top_margin_in_inches * 72 if header_top_margin_in_inches else 100
                    img = Image(img_path, width=600, height=header_top_margin_in_pixels)
                else:
                    link="/staticfiles/media/header_images/Default.jpg"
                    updated_link = link.replace('/staticfiles/', '/static/')
                    img_path="http://13.233.211.102/doctor"+updated_link
                    header_top_margin_in_inches = (float(prescription_settings['header_top_margin']) if prescription_settings['header_top_margin'] else 0)
                    header_top_margin_in_pixels = header_top_margin_in_inches * 72 if header_top_margin_in_inches else 100
                    img = Image(img_path, width=600, height=header_top_margin_in_pixels)

            elif(prescription_settings['header_type']==1):
                options=['clinic_name','clinic_address','doctor_name','doctor_degree','doctor_speciality','doctor_availability','clinic_services','clinic_logo','clinic_mobile_number']
                checked_options=[]
                for option in options:
                    if(prescription_settings[option]):
                        checked_options.append(option)
                        
                print(checked_options)
            else:
                img=0
    else:
            print(detail_response.json().get('message_code'))
            prescription_settings=0
            print(prescription_settings)
            img_path = 'img/logo1.jpg'
            img = Image(img_path, width=50, height=50)
    pdf_buffer = BytesIO()
    left_margin = 0
    right_margin = 0
    print("page_size",pagesize)
    my_doc = SimpleDocTemplate(pdf_buffer, pagesize=pagesize, topMargin=0, leftMargin=left_margin, rightMargin=right_margin)
    line_break = Spacer(1, 12)
    styles = getSampleStyleSheet()
    center_style = ParagraphStyle(
        'CenterHeading1',
        parent=styles['Heading1'],
        alignment=1,  # 0=left, 1=center, 2=right
    )

    if result_doctor:
        first_doctor_data = result_doctor[0]
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
        education = str(basic_education) +", "+str(additional_education)
    else:
        first_doctor_data = ""
        doctor_firstname = ""
        doctor_lastname = ""
        doctor_registrationno = ""
        doctor_address =  ""
        doctor_mobileno =  ""
        doctor_email =  ""
        doctor_pincode = ""
        basic_education =  ""
        additional_education =  ""
        services_offered =  ""
        education = ""
        
    if result_doctor_location:
        location_title = result_doctor_location['location_title']
    else:
        location_title = ""
    heading_text = "<font size=18 color=black><b>"+str(location_title)+"</b></font>"
    heading = Paragraph(heading_text, center_style)
    hr_line = HRFlowable(width="100%", color=colors.black, thickness=2, spaceBefore=10, spaceAfter=10)
    
    drinfoblock = "<font size=15 color=black><b>" + str(doctor_firstname) + "&nbsp;"+str(doctor_lastname)+"</b></font> "
    
    if result_doctor_location_availability["availability_day"]:
        availability_day = result_doctor_location_availability["availability_day"]
    else:
        availability_day =""
    if availability_day == 1:
        daytime= str(result_doctor_location_availability["availability_starttime"])+"-"+str(result_doctor_location_availability["availability_endtime"])
    else:
        daytime=""

    if result_doctor_location_availability["availability_order"]:
        availability_order = result_doctor_location_availability["availability_order"]
    else:
        availability_order = ""

    if availability_order == 1:
        ordertime = "Morning"
    elif availability_order == 2:
        ordertime = "Afternoon"
    elif availability_order == 3:
        ordertime = "Evening"
    else:
        ordertime = ""
    
    hindi_style = ParagraphStyle(
        'HindiText',
        parent=styles['BodyText'],
        fontSize=12,
    )
    if result_doctor_location['services_offered_at']:
        services_offered_at = result_doctor_location['services_offered_at']
    else:
        services_offered_at = ""
    hindi_text = "नमस्ते, यह एक उदाहरण है!"

    if(prescription_settings):
            if(prescription_settings['header_type']==1):
                table_data=[]
                
                # if('doctor_name' in checked_options):
                #     table_data.extend([[Paragraph(drinfoblock, styles['BodyText']), Paragraph(services_offered_at, styles['BodyText'])]])
                # if('clinic_name' in checked_options):
                #     table_data.extend([[Paragraph(str(location_title)+"", styles['BodyText'])]])
                # if('clinic_address' in checked_options):
                #     table_data.extend([ [Paragraph(" "+str(result_doctor_location['location_address'])+"", styles['BodyText'])]])
                # if('doctor_availability' in checked_options):
                #     table_data.extend([[Paragraph("Time: "+str(ordertime)+" "+str(daytime)+"", styles['BodyText'])]])
                # if('clinic_mobile_number' in checked_options):
                #     table_data.extend([[Paragraph("Mob. No.:"+str(doctor_mobileno)+"", styles['BodyText'])]])
                
                # table_data.extend([[Paragraph("Regd. No. "+str(doctor_registrationno)+"", styles['BodyText'])]])
                if 'doctor_name' in checked_options:
                    table_data.append([Paragraph(drinfoblock, styles['BodyText']), Paragraph(services_offered_at, styles['BodyText'])])
                else:
                    drinfoblock = "<font size=15 color=black><b>" + " " + "&nbsp;"+" "+"</b></font> "
                    table_data.append([Paragraph(drinfoblock, styles['BodyText']), Paragraph(services_offered_at, styles['BodyText'])])

                if 'clinic_name' in checked_options:
                    table_data.append([Paragraph(str(location_title), styles['BodyText'])])

                if 'clinic_address' in checked_options:
                    table_data.append([Paragraph(" " + str(result_doctor_location['location_address']), styles['BodyText'])])

                if 'doctor_availability' in checked_options:
                    table_data.append([Paragraph("Time: " + str(ordertime) + " " + str(daytime), styles['BodyText'])])

                if 'clinic_mobile_number' in checked_options:
                    table_data.append([Paragraph("Mob. No.:" + str(doctor_mobileno), styles['BodyText'])])

                table_data.append([Paragraph("Regd. No. " + str(doctor_registrationno), styles['BodyText'])])

            else:
               table_data=[[Paragraph("")]]
    
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

            table = Table(table_data, style=table_style, colWidths=[415, 165])
            # print(table)
            if(prescription_settings['header_type']==2):
                hr_line = HRFlowable(width="100%", color=colors.black, thickness=2,spaceBefore=0, spaceAfter=2)
                flowables = [img, table]

            elif(prescription_settings['header_type']==1):
                table = Table(table_data, style=table_style, colWidths=[415, 165])
                hr_line = HRFlowable(width="100%", color=colors.black, thickness=2,spaceBefore=2, spaceAfter=2)
                if('clinic_logo' in checked_options):
                    api_url="http://13.233.211.102/doctor/api/get_all_doctor_location/"
                    response=requests.post(api_url,json={"doctor_location_id":result_doctor_location.get('doctor_location_id')})
                    data=response.json().get("message_data",{})
                    # print(data)
                    link=(data[0]).get('location_image')
                    if(link is None):
                        link="/staticfiles/media/location_images/cliniclogo2.jpg"
                    # Replace '/staticfiles/' with '/static/'
                    updated_link = link.replace('/staticfiles/', '/static/')
                    img_path="http://13.233.211.102/doctor"+updated_link
                    #img = Image(img_path, width=100, height=100)
                    img_table = create_aligned_image_table(img_path,prescription_settings['clinic_logo_alignment'], width=50, height=50)  # Change 'center' to 'left' or 'right' based on your input
                    flowables = [img_table,table, hr_line]
                else:
                    heading = Paragraph(heading_text, center_style)
                    flowables = [heading,table, hr_line]
                
            
            else:
                # header_top_margin=int(prescription_settings['header_top_margin'])
                header_top_margin = (float(prescription_settings['header_top_margin']) if prescription_settings['header_top_margin'] else 0) * 72.0
                hr_line = HRFlowable(width="100%", color=colors.black, thickness=2, spaceBefore=header_top_margin, spaceAfter=2)
                flowables = [table,hr_line]
    
    else:
        print("no prescription setting avaliable")
        table_data = [
                    [Paragraph(drinfoblock, styles['BodyText']), Paragraph(services_offered_at, styles['BodyText'])],
                    [Paragraph(""+"", styles['BodyText'])], 
                    [Paragraph("Regd. No. "+str(doctor_registrationno)+"", styles['BodyText'])],
                    [Paragraph("<font size=10 color=black><b>"+"</b></font>", styles['BodyText'])],
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
        table = Table(table_data, style=table_style, colWidths=[415, 165])
        hr_line = HRFlowable(width="100%", color=colors.black, thickness=2,spaceBefore=2, spaceAfter=2)
        flowables = [heading,table, hr_line]
         
         

    
    if result_patient:
        first_patient_data = result_patient
        patient_firstname = first_patient_data.get('patient_firstname',"")
        patient_fateherhusbandname = first_patient_data.get('patient_fateherhusbandname',"")
        patient_lastname = first_patient_data.get('patient_lastname',"")
        # full_name = str(patient_firstname + " " + patient_fateherhusbandname + " " + patient_lastname)
        full_name = ""

        if patient_firstname:
            full_name += patient_firstname.strip()  # strip() to remove any leading/trailing whitespace

        if patient_fateherhusbandname:
            if full_name:
                full_name += " "  # Add space if first name is not empty
            full_name += patient_fateherhusbandname.strip()

        if patient_lastname:
            if full_name:
                full_name += " "  # Add space if first or father/husband name is not empty
            full_name += patient_lastname.strip()
            
        patient_gender = first_patient_data.get('patient_gender',"")
    else:
        first_patient_data = ""
        patient_firstname = ""
        patient_fateherhusbandname = ""
        patient_lastname = ""
        full_name = ""
        patient_gender = ""
    
    if patient_gender==0:
        gender = "Male"
    else:
        gender = "Female"
    if first_patient_data.get('patient_mobileno',""):
        patient_mobileno = first_patient_data.get('patient_mobileno',"")
    else:
        patient_mobileno = ""
    
    Patient = "<font size=10 color=black><b>Patient's Name: "+str(full_name)+"     "+str(gender)+"</b></font>"
    current_date = datetime.now()
    formatted_date = current_date.strftime(" %b %d, %Y")
    # current_time = datetime.now().time()
    # print('current time',current_time)
    # formatted_time = current_time.strftime("%I:%M %p")
    # print('formatted time',formatted_time)
    # Set the desired time zone, e.g., 'Asia/Kolkata' or 'America/New_York'
    time_zone = pytz.timezone('Asia/Kolkata')

    # Get the current time in the specified time zone
    current_time = datetime.now(time_zone)
    # print('current time', current_time)

    # Format the time
    formatted_time = current_time.strftime("%I:%M %p")
    # print('formatted time', formatted_time)
    Date = "<font size=10 color=black><b>Date: &nbsp;"+str(formatted_date)+",</b></font>"
    Time = "<font size=10 color=black><b>"+str(formatted_time)+"</b></font>"
    hr_line_white = HRFlowable(width="100%", color=colors.white, thickness=2, spaceBefore=6, spaceAfter=4)


    # opd
    if result_consultation:
        appointment_id = result_consultation[0].get('appointment_id','')
    else:
        appointment_id = ""
    if appointment_id:
        formatted_appointment_id = (
            '0' + str(appointment_id) if 1 <= appointment_id <= 9 else str(appointment_id)
        )
    else:
        formatted_appointment_id=""

    current_month = datetime.now().strftime("%m")
    current_day = datetime.now().strftime("%d")
    opd_appointment_no = str(current_month)+str(current_day)+str(formatted_appointment_id)
    new_table_data = [
        [Paragraph(Patient, styles['BodyText']), Paragraph(Date, styles['BodyText'])],
        [Paragraph("Opd No:"+opd_appointment_no+" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  Mob.:"+str(patient_mobileno)+"", styles['BodyText']), Paragraph(Time, styles['BodyText'])],
        # [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;", styles['BodyText']), Paragraph("", styles['BodyText'])],
        # [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;", styles['BodyText']), Paragraph("", styles['BodyText'])],
        # [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;", styles['BodyText']), Paragraph("", styles['BodyText'])],
        # [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;", styles['BodyText']), Paragraph("", styles['BodyText'])],
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
    new_table = Table(new_table_data, style=table_style_second, colWidths=[415, 165])
    flowables.extend([new_table, hr_line_white])
    OE =  "<font size=10 color=black><b>O/E :-</b></font>"
    
    if result_patientvitals:
        patient_heartratepluse = result_patientvitals['patient_heartratepluse']
        patient_bpsystolic = result_patientvitals['patient_bpsystolic']
        patient_bpdistolic = result_patientvitals['patient_bpdistolic']
        patient_painscale = result_patientvitals['patient_painscale']
        patient_respiratoryrate = result_patientvitals['patient_respiratoryrate']
        patient_temparature = result_patientvitals['patient_temparature']
        patient_chest = result_patientvitals['patient_chest']
        patient_ecg = result_patientvitals['patient_ecg']
        patient_height=result_patientvitals['height']
        patient_weight=result_patientvitals['weight']
        bp = str(patient_bpsystolic) +"/"+str(patient_bpdistolic)
    else:
        patient_heartratepluse = ""
        patient_bpsystolic = ""
        patient_bpdistolic = ""
        patient_painscale = ""
        patient_respiratoryrate = ""
        patient_temparature = ""
        patient_chest = ""
        patient_ecg = ""
        bp = ""
        patient_height=""
        patient_weight=""
    
    medicine_str = "<font size=10 color=black><b>Rx :- </b></font><br/>"  # Initialize an empty string to store medicine names
    # print(result_patient_medications)
    for medication in result_patient_medications:
        medicine_str += str(medication["medicine_name"])+"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+ str(medication["medicine_duration"])+"D "+ "<br/>"
        medicine_str += str(str(medication["medicine_doses"])+"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+str(medication["doctor_instruction_text"]))+ "<br/>"
        # medicine_str += str(medication["medicine_doses"]) + "<br/><br/>"
        # medicine_str += str(medication["doctor_instruction_text"]) + "<br/><br/>"
         
    new_table_data_three = [
        [Paragraph("Wt&nbsp;:&nbsp;&nbsp;&nbsp;"+str(patient_weight)+"", styles['BodyText']), Paragraph(OE, styles['BodyText']), Paragraph(medicine_str, styles['BodyText'])],
        [Paragraph("Ht&nbsp;:&nbsp;&nbsp;&nbsp; "+str(patient_height)+"", styles['BodyText']), Paragraph("Pulse &nbsp;:&nbsp;&nbsp;&nbsp; "+str(patient_heartratepluse)+"/min" , styles['BodyText'])],
        [Paragraph("Hr&nbsp;:&nbsp;&nbsp;&nbsp;"+str(patient_heartratepluse)+"", styles['BodyText']), Paragraph("Temp&nbsp;:&nbsp;&nbsp;&nbsp; "+str(patient_temparature)+"", styles['BodyText'])],
        [Paragraph("Bp&nbsp;:&nbsp;&nbsp;&nbsp;"+str(bp)+"", styles['BodyText']),],
        [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;", styles['BodyText'])],
        [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
        [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
        # [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
        # [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
        # [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
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
        ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
        ('VALIGN', (2, 0), (2, -1), 'TOP'),
        ('SPAN', (2, 0), (2, -1)),
    ])
     
    # print(result_consultation)
    new_table_three = Table(new_table_data_three, style=new_table_style, colWidths=[193, 193, 193])
    flowables.extend([new_table_three, hr_line_white])
    Advice =  "<font size=10 color=black><b>Advice :-</b></font>"

    new_table_data_four = [
        [Paragraph(Advice, styles['BodyText']), Paragraph("<font size=10 color=black><b>Instruction :-</b></font>"+result_consultation[0]['instructions'], styles['BodyText'])],
        [Paragraph(result_findings_symptoms[0].get('advice'), styles['BodyText']), Paragraph("", styles['BodyText'])],
        # [Paragraph("C.T. Scan", styles['BodyText']), Paragraph("Review after 4 Days on Mar 28, 2023" , styles['BodyText'])],
        # [Paragraph("Paracheck for MPÐ", styles['BodyText']), Paragraph("" , styles['BodyText'])],
        # [Paragraph("CBC", styles['BodyText']), Paragraph("" , styles['BodyText'])],
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
    
    new_table_four = Table(new_table_data_four, style=new_table_style_four, colWidths=[290,290])
    flowables.extend([new_table_four, hr_line_white])
    #fourth section end
    my_doc.build(flowables)
    return pdf_buffer
 
 

def create_aligned_image_table(image_path, alignment=0, width=50, height=50):
    img = Image(image_path,width,height)
    if alignment == 2:  # Center
        table_data = [["", img, ""]]
        table_style = TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),    # Set top padding to 0
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0), # Set bottom padding to 0
            ('LEFTPADDING', (0, 0), (-1, -1), 0),   # Set left padding to 0 (optional)
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Set right padding to 0 (optional)
            ('TOPMARGIN', (0, 0), (-1, -1), 0),     # Set top margin to 0
            ('BOTTOMMARGIN', (0, 0), (-1, -1), 0)   # Set bottom margin to 0
        ])
    elif alignment == 1:  # Left
        table_data = [[img, ""]]
        table_style = TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),    # Set top padding to 0
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0), # Set bottom padding to 0
            ('LEFTPADDING', (0, 0), (-1, -1), 0),   # Set left padding to 0 (optional)
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Set right padding to 0 (optional)
            ('TOPMARGIN', (0, 0), (-1, -1), 0),     # Set top margin to 0
            ('BOTTOMMARGIN', (0, 0), (-1, -1), 0)   # Set bottom margin to 0
        ])
    elif alignment == 3:  # Right
        table_data = [["", img]]
        table_style = TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),    # Set top padding to 0
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0), # Set bottom padding to 0
            ('LEFTPADDING', (0, 0), (-1, -1), 0),   # Set left padding to 0 (optional)
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Set right padding to 0 (optional)
            ('TOPMARGIN', (0, 0), (-1, -1), 0),     # Set top margin to 0
            ('BOTTOMMARGIN', (0, 0), (-1, -1), 0)   # Set bottom margin to 0
        ])
    else:
        raise ValueError("Invalid alignment option")

    # Setting column widths to ensure image alignment
    if(alignment==1):
        width=150
    elif(alignment==3):
        width=250
    col_widths = [width + 4*inch if alignment == 1 else width,width,width + 4*inch if alignment == 3 else width]

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(table_style)
    return table


 
##################################################################clinic pdf
    
@api_view(['POST'])
def fi_generateclinicpdf(request):
    print("543")

    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    
    doctor_location_id = request.data.get('doctor_location_id', None)
    if not doctor_location_id:
        res = {'message_code': 999, 'message_text': 'doctor location id is required.'}
    else:
        try:
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
            
            if result_doctor_location:
                doctor_id = result_doctor_location[0]['doctor_id']
            else:
                doctor_id=""
            
            if doctor_id:
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
            else:
                result_doctor = []   
            
            if doctor_location_id and doctor_id:
                # Retrieve a single instance of Tbldoctorlocationavailability
                instance = Tbldoctorlocationavailability.objects.filter(doctor_location_id=doctor_location_id, doctor_id=doctor_id, isdeleted=0).order_by('doctor_location_availability_id').first()
                if instance:
                    # Serialize the single instance
                    serializer = DoctorLocationAvailabilitySerializer(instance)
                    result_doctor_location_availability = serializer.data
                else:
                    result_doctor_location_availability = []
            else:
                result_doctor_location_availability = []

            if result_doctor_location:
             # Generate PDF
                pdf_buffer = generate_clinic_pdf(result_doctor_location,result_doctor,result_doctor_location_availability)
                pdf_value = pdf_buffer.getvalue()
                pdf_buffer.close()
                
    
                pdf_filename = f"{doctor_id}{doctor_location_id}.pdf"

                pdf_path = os.path.join(settings.PDF_ROOT, pdf_filename)

                file_path = default_storage.save(pdf_path, ContentFile(pdf_value))
                absolute_file_path = default_storage.path(file_path)

                # Convert the path to a string without hyperlink
                final_path = str(absolute_file_path.replace('\\', '/'))
                
                url_prefix = "http://13.233.211.102/medicalrecord/static/"
                url = final_path.replace("/home/ubuntu/medicalrecord/staticfiles/", url_prefix)
                res = {
                    'message_code': 1000,
                    'message_text': "clinic pdf generated successfully.",
                    'message_data':  [{'pdf_url': url}],
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }
            else:
                res = {
                    'message_code': 999,
                    'message_text': "clinic pdf generation failed, doctor_location_id not found.",
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
    
    if result_doctor_location:
        location_title = result_doctor_location[0].get('location_title', None)
    else:
        location_title = ""

    content_text = "<font size=18 color=black><b>"+str(location_title)+"</b></font>"
    if content_text:
        marathi_translation = translate_to_marathi(content_text)
    else:
        marathi_translation=""
    
    
    if result_doctor:
        first_doctor_data = result_doctor[0]
        doctor_firstname = first_doctor_data.get('doctor_firstname',"")
        doctor_lastname = first_doctor_data.get('doctor_lastname',"")
        doctor_registrationno = first_doctor_data.get('doctor_registrationno',"")
        doctor_address =  first_doctor_data.get('doctor_address',"")
        doctor_firstname_marathi = translate_to_marathi(doctor_firstname)
        doctor_lastname_marathi = translate_to_marathi(doctor_lastname)
        doctor_address_marathi = translate_to_marathi(doctor_address)
    else:
        doctor_firstname = ""
        doctor_lastname = ""
        doctor_registrationno = ""
        doctor_address =  ""
        doctor_firstname_marathi = ""
        doctor_lastname_marathi = ""
        doctor_address_marathi = ""

    hindi_style_address = ParagraphStyle(
        'HindiText',
        parent=styles['BodyText'],
        fontName='Mangal',  # Use the Mangal font
        fontSize=15,
    )
    
    content_style_eng = ParagraphStyle(name='Content', fontSize=15)
    styles = getSampleStyleSheet()
    content_style = ParagraphStyle(name='Content', fontSize=25, leading=14,topMargin=0)
    # Create image
    img = Image(img_path, width=100, height=100)
    data = [[img,Paragraph(content_text, content_style), Paragraph(marathi_translation, hindi_style)],
             [Paragraph("", content_style), Paragraph(doctor_address, content_style_eng),Paragraph(doctor_address_marathi, hindi_style_address)],
            ]
    table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'LEFT'),  # Vertical alignment in the middle
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),  # Alignment of the content to the left
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),  # Bottom padding  # Add grid lines
    ])
    table = Table(data, style=table_style)
    flowables = [table]
    
    drtimefont = ParagraphStyle(
        'HindiText',
        parent=styles['BodyText'],
        fontName='Mangal',  # Use the Mangal font
        fontSize=15,
    )
    
    if doctor_firstname and doctor_lastname:
        drfullnmeng = str(doctor_firstname)+" "+str(doctor_lastname)
    else:
        drfullnmeng =""

    if doctor_firstname_marathi and doctor_lastname_marathi:
        drfullnmmarathi = str(doctor_firstname_marathi)+" "+str(doctor_lastname_marathi)
    else:
        drfullnmmarathi=""
    
    opdtimingmarathi = "दवाखान्यांची वेळ"
    content_style_time = ParagraphStyle(name='Content', fontSize=15, leading=14)
    
    if result_doctor_location_availability:
        availability_day = result_doctor_location_availability["availability_day"]
    else:
        availability_day = ""
     
    if availability_day == 1:
        daytime= str(result_doctor_location_availability["availability_starttime"])+"-"+str(result_doctor_location_availability["availability_endtime"])
    else:
        daytime=""
        
    if result_doctor_location_availability:
        availability_order = result_doctor_location_availability["availability_order"]
    else:
        availability_order=""
    
    # Check the value of 'availability_order'
    if availability_order == 1:
        ordertime = "Morning"
    elif availability_order == 2:
        ordertime = "Afternoon"
    elif availability_order == 3:
        ordertime = "Evening"
    else:
        ordertime = ""
    
    if ordertime and daytime:
        timemeng = str(ordertime)+" "+str(daytime)
    else:
        timemeng = ""
    
    if timemeng:
        timemarathi=translate_to_marathi(timemeng)
    else:
        timemarathi=""

    table_data = [
        [ Paragraph(drfullnmmarathi, hindi_style),Paragraph(drfullnmeng, content_style)],
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
    if result_doctor_location[0]['location_qr_url']:
        location_qr_url = result_doctor_location[0]['location_qr_url']
        url = location_qr_url
    else:
        url=""

    if url:
        styles = getSampleStyleSheet()
        qr_code_image = generate_qr_code(url)
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        img = Image(qr_code_image, width=400, height=400)
    else:
        img=""
    if img:
        flowables.extend([img])  # Wrap the image object in a list and extend
    else:
        flowables.extend("")
    
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





# def generate_pdf(result_doctor,result_patient,result_doctor_location,result_patientvitals,result_doctor_location_availability,result_patient_medications,result_consultation,result_findings_symptoms):
    
#     pdf_buffer = BytesIO()
#     left_margin = 0
#     right_margin = 0
#     my_doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0, leftMargin=left_margin, rightMargin=right_margin)
#     line_break = Spacer(1, 12)
#     styles = getSampleStyleSheet()
#     center_style = ParagraphStyle(
#         'CenterHeading1',
#         parent=styles['Heading1'],
#         alignment=1,  # 0=left, 1=center, 2=right
#     )

#     if result_doctor:
#         first_doctor_data = result_doctor[0]
#         doctor_firstname = first_doctor_data.get('doctor_firstname',"")
#         doctor_lastname = first_doctor_data.get('doctor_lastname',"")
#         doctor_registrationno = first_doctor_data.get('doctor_registrationno',"")
#         doctor_address =  first_doctor_data.get('doctor_address',"")
#         doctor_mobileno =  first_doctor_data.get('doctor_mobileno',"")
#         doctor_email =  first_doctor_data.get('doctor_email',"")
#         doctor_pincode =  first_doctor_data.get('doctor_pincode',"")
#         basic_education =  first_doctor_data.get('basic_education',"")
#         additional_education =  first_doctor_data.get('additional_education',"")
#         services_offered =  first_doctor_data.get('services_offered',"")
#         education = str(basic_education) +", "+str(additional_education)
#     else:
#         first_doctor_data = ""
#         doctor_firstname = ""
#         doctor_lastname = ""
#         doctor_registrationno = ""
#         doctor_address =  ""
#         doctor_mobileno =  ""
#         doctor_email =  ""
#         doctor_pincode = ""
#         basic_education =  ""
#         additional_education =  ""
#         services_offered =  ""
#         education = ""
        
#     if result_doctor_location:
#         location_title = result_doctor_location['location_title']
#     else:
#         location_title = ""
#     heading_text = "<font size=18 color=black><b>"+str(location_title)+"</b></font>"
#     heading = Paragraph(heading_text, center_style)
#     hr_line = HRFlowable(width="100%", color=colors.black, thickness=2, spaceBefore=10, spaceAfter=10)
    
#     drinfoblock = "<font size=15 color=black><b>" + str(doctor_firstname) + "&nbsp;"+str(doctor_lastname)+"</b></font> "
    
#     if result_doctor_location_availability["availability_day"]:
#         availability_day = result_doctor_location_availability["availability_day"]
#     else:
#         availability_day =""
#     if availability_day == 1:
#         daytime= str(result_doctor_location_availability["availability_starttime"])+"-"+str(result_doctor_location_availability["availability_endtime"])
#     else:
#         daytime=""

#     if result_doctor_location_availability["availability_order"]:
#         availability_order = result_doctor_location_availability["availability_order"]
#     else:
#         availability_order = ""

#     if availability_order == 1:
#         ordertime = "Morning"
#     elif availability_order == 2:
#         ordertime = "Afternoon"
#     elif availability_order == 3:
#         ordertime = "Evening"
#     else:
#         ordertime = ""
    
#     hindi_style = ParagraphStyle(
#         'HindiText',
#         parent=styles['BodyText'],
#         fontSize=12,
#     )
#     if result_doctor_location['services_offered_at']:
#         services_offered_at = result_doctor_location['services_offered_at']
#     else:
#         services_offered_at = ""
#     hindi_text = "नमस्ते, यह एक उदाहरण है!"
#     table_data = [
#         [Paragraph(drinfoblock, styles['BodyText']), Paragraph(services_offered_at, styles['BodyText'])],
#         [Paragraph(""+education+"", styles['BodyText'])], 
#         [Paragraph("Regd. No. "+str(doctor_registrationno)+"", styles['BodyText'])],
#         [Paragraph("<font size=10 color=black><b>"+str(services_offered)+"</b></font>", styles['BodyText'])],
#         [Paragraph("Time: "+str(ordertime)+" "+str(daytime)+"", styles['BodyText'])],
#         [Paragraph(" "+str(doctor_address)+" Pin:"+str(doctor_pincode)+"", styles['BodyText'])],
#         [Paragraph("Mob. No.:"+str(doctor_mobileno)+"", styles['BodyText'])],
#         [Paragraph("E-mail:"+str(doctor_email)+"", styles['BodyText'])],
#     ]
    
#     table_style = TableStyle([
#         ('GRID', (0, 0), (-1, -1), 1, colors.white),
#         ('BOX', (0, 0), (-1, -1), 1, colors.white),
#         ('PADDING', (0, 0), (-1, 0), 5),
#         ('PADDING', (0, 1), (-1, -1), 0),
#         ('LEFTPADDING', (0, 0), (-1, 0), 0),
#         ('LEFTPADDING', (0, 1), (-1, -1), 0),
#         ('RIGHTPADDING', (0, 0), (-1, 0), 0),
#         ('RIGHTPADDING', (0, 1), (-1, -1), 0),
#         ('TOPPADDING', (0, 0), (-1, 0), 5),
#         ('TOPPADDING', (0, 1), (-1, -1), 0),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
#         ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
#         ('VALIGN', (1, 0), (1, -1), 'TOP'),  # Align second column to the top
#         ('SPAN', (1, 0), (1, -1)),
#     ])

#     table = Table(table_data, style=table_style, colWidths=[415, 165])
#     flowables = [heading, table, hr_line]
    
#     if result_patient:
#         first_patient_data = result_patient
#         patient_firstname = first_patient_data.get('patient_firstname',"")
#         patient_fateherhusbandname = first_patient_data.get('patient_fateherhusbandname',"")
#         patient_lastname = first_patient_data.get('patient_lastname',"")
#         # full_name = str(patient_firstname + " " + patient_fateherhusbandname + " " + patient_lastname)
#         full_name = ""

#         if patient_firstname:
#             full_name += patient_firstname.strip()  # strip() to remove any leading/trailing whitespace

#         if patient_fateherhusbandname:
#             if full_name:
#                 full_name += " "  # Add space if first name is not empty
#             full_name += patient_fateherhusbandname.strip()

#         if patient_lastname:
#             if full_name:
#                 full_name += " "  # Add space if first or father/husband name is not empty
#             full_name += patient_lastname.strip()
            
#         patient_gender = first_patient_data.get('patient_gender',"")
#     else:
#         first_patient_data = ""
#         patient_firstname = ""
#         patient_fateherhusbandname = ""
#         patient_lastname = ""
#         full_name = ""
#         patient_gender = ""
    
#     if patient_gender==0:
#         gender = "Male"
#     else:
#         gender = "Female"
#     if first_patient_data.get('patient_mobileno',""):
#         patient_mobileno = first_patient_data.get('patient_mobileno',"")
#     else:
#         patient_mobileno = ""
    
#     Patient = "<font size=10 color=black><b>Patient's Name: "+str(full_name)+"   N/A "+str(gender)+"</b></font>"
#     current_date = datetime.now()
#     formatted_date = current_date.strftime(" %b %d, %Y")
#     current_time = datetime.now().time()
#     formatted_time = current_time.strftime("%I:%M %p")
#     Date = "<font size=10 color=black><b>Date: &nbsp;"+str(formatted_date)+",</b></font>"
#     Time = "<font size=10 color=black><b>"+str(formatted_time)+"</b></font>"
#     hr_line_white = HRFlowable(width="100%", color=colors.white, thickness=2, spaceBefore=10, spaceAfter=10)

#     # opd
#     if result_consultation:
#         appointment_id = result_consultation[0].get('appointment_id','')
#     else:
#         appointment_id = ""
#     if appointment_id:
#         formatted_appointment_id = (
#             '0' + str(appointment_id) if 1 <= appointment_id <= 9 else str(appointment_id)
#         )
#     else:
#         formatted_appointment_id=""

#     current_month = datetime.now().strftime("%m")
#     current_day = datetime.now().strftime("%d")
#     opd_appointment_no = str(current_month)+str(current_day)+str(formatted_appointment_id)
#     new_table_data = [
#         [Paragraph(Patient, styles['BodyText']), Paragraph(Date, styles['BodyText'])],
#         [Paragraph("Opd No:"+opd_appointment_no+" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  Mob.:"+str(patient_mobileno)+"", styles['BodyText']), Paragraph(Time, styles['BodyText'])],
#         [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;", styles['BodyText']), Paragraph("", styles['BodyText'])],
#         # [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;", styles['BodyText']), Paragraph("", styles['BodyText'])],
#         # [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;", styles['BodyText']), Paragraph("", styles['BodyText'])],
#         # [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;", styles['BodyText']), Paragraph("", styles['BodyText'])],
#     ]

#     table_style_second = TableStyle([
#         ('GRID', (0, 0), (-1, -1), 1, colors.white),
#         ('BOX', (0, 0), (-1, -1), 1, colors.white),
#         ('PADDING', (0, 0), (-1, 0), 5),
#         ('PADDING', (0, 1), (-1, -1), 0),
#         ('LEFTPADDING', (0, 0), (-1, 0), 0),
#         ('LEFTPADDING', (0, 1), (-1, -1), 0),
#         ('RIGHTPADDING', (0, 0), (-1, 0), 0),
#         ('RIGHTPADDING', (0, 1), (-1, -1), 0),
#         ('TOPPADDING', (0, 0), (-1, 0), 5),
#         ('TOPPADDING', (0, 1), (-1, -1), 0),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
#         ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
#     ])
#     new_table = Table(new_table_data, style=table_style_second, colWidths=[415, 165])
#     flowables.extend([new_table, hr_line_white])
#     OE =  "<font size=10 color=black><b>O/E :-</b></font>"
    
#     if result_patientvitals:
#         patient_heartratepluse = result_patientvitals['patient_heartratepluse']
#         patient_bpsystolic = result_patientvitals['patient_bpsystolic']
#         patient_bpdistolic = result_patientvitals['patient_bpdistolic']
#         patient_painscale = result_patientvitals['patient_painscale']
#         patient_respiratoryrate = result_patientvitals['patient_respiratoryrate']
#         patient_temparature = result_patientvitals['patient_temparature']
#         patient_chest = result_patientvitals['patient_chest']
#         patient_ecg = result_patientvitals['patient_ecg']
#         patient_height=result_patientvitals['height']
#         patient_weight=result_patientvitals['weight']
#         bp = str(patient_bpsystolic) +"/"+str(patient_bpdistolic)
#     else:
#         patient_heartratepluse = ""
#         patient_bpsystolic = ""
#         patient_bpdistolic = ""
#         patient_painscale = ""
#         patient_respiratoryrate = ""
#         patient_temparature = ""
#         patient_chest = ""
#         patient_ecg = ""
#         bp = ""
#         patient_height=""
#         patient_weight=""
    
#     medicine_str = "<font size=10 color=black><b>Rx :- </b></font><br/>"  # Initialize an empty string to store medicine names
#     # print(result_patient_medications)
#     for medication in result_patient_medications:
#         medicine_str += str(medication["medicine_name"])+" "+ str(medication["medicine_duration"])+"D "+str(medication["medicine_doses"])+" "+str(medication["doctor_instruction_text"])+ "<br/>"
#         # medicine_str += str(medication["medicine_doses"]) + "<br/><br/>"
#         # medicine_str += str(medication["doctor_instruction_text"]) + "<br/><br/>"
#     new_table_data_three = [
#         [Paragraph("Wt&nbsp;:&nbsp;&nbsp;&nbsp;"+str(patient_weight)+"", styles['BodyText']), Paragraph(OE, styles['BodyText']), Paragraph(medicine_str, styles['BodyText'])],
#         [Paragraph("Ht&nbsp;:&nbsp;&nbsp;&nbsp; "+str(patient_height)+"", styles['BodyText']), Paragraph("Pulse &nbsp;:&nbsp;&nbsp;&nbsp; "+str(patient_heartratepluse)+"/min" , styles['BodyText'])],
#         [Paragraph("Hr&nbsp;:&nbsp;&nbsp;&nbsp;"+str(patient_heartratepluse)+"", styles['BodyText']), Paragraph("Temp&nbsp;:&nbsp;&nbsp;&nbsp; "+str(patient_temparature)+"", styles['BodyText'])],
#         [Paragraph("Bp&nbsp;:&nbsp;&nbsp;&nbsp;"+str(bp)+"", styles['BodyText']),],
#         [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;", styles['BodyText'])],
#         [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
#         # [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
#         # [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
#         # [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
#         # [Paragraph("", styles['BodyText']), Paragraph("&nbsp;&nbsp;&nbsp;&nbsp; ", styles['BodyText'])],
#     ]

#     new_table_style = TableStyle([
#         ('GRID', (0, 0), (-1, -1), 1, colors.white),
#         ('BOX', (0, 0), (-1, -1), 1, colors.white),
#         ('PADDING', (0, 0), (-1, 0), 0),
#         ('PADDING', (0, 1), (-1, -1), 0),
#         ('LEFTPADDING', (0, 0), (-1, 0), 0),
#         ('LEFTPADDING', (0, 1), (-1, -1), 0),
#         ('RIGHTPADDING', (0, 0), (-1, 0), 0),
#         ('RIGHTPADDING', (0, 1), (-1, -1), 0),
#         ('TOPPADDING', (0, 0), (-1, 0), 0),
#         ('TOPPADDING', (0, 1), (-1, -1), 0),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
#         ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
#         ('VALIGN', (2, 0), (2, -1), 'TOP'),
#         ('SPAN', (2, 0), (2, -1)),
#     ])
#     # print(result_consultation)
#     new_table_three = Table(new_table_data_three, style=new_table_style, colWidths=[193, 193, 193])
#     flowables.extend([new_table_three, hr_line_white])
#     Advice =  "<font size=10 color=black><b>Advice :-</b></font>"

#     new_table_data_four = [
#         [Paragraph(Advice, styles['BodyText']), Paragraph("<font size=10 color=black><b>Instruction :-</b></font>"+result_consultation[0]['instructions'], styles['BodyText'])],
#         [Paragraph(result_findings_symptoms[0].get('advice'), styles['BodyText']), Paragraph("", styles['BodyText'])],
#         # [Paragraph("C.T. Scan", styles['BodyText']), Paragraph("Review after 4 Days on Mar 28, 2023" , styles['BodyText'])],
#         # [Paragraph("Paracheck for MPÐ", styles['BodyText']), Paragraph("" , styles['BodyText'])],
#         # [Paragraph("CBC", styles['BodyText']), Paragraph("" , styles['BodyText'])],
#     ]

#     new_table_style_four = TableStyle([
#         ('GRID', (0, 0), (-1, -1), 1, colors.white),
#         ('BOX', (0, 0), (-1, -1), 1, colors.white),
#         ('PADDING', (0, 0), (-1, 0), 0),
#         ('PADDING', (0, 1), (-1, -1), 0),
#         ('LEFTPADDING', (0, 0), (-1, 0), 0),
#         ('LEFTPADDING', (0, 1), (-1, -1), 0),
#         ('RIGHTPADDING', (0, 0), (-1, 0), 0),
#         ('RIGHTPADDING', (0, 1), (-1, -1), 0),
#         ('TOPPADDING', (0, 0), (-1, 0), 0),
#         ('TOPPADDING', (0, 1), (-1, -1), 0),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
#         ('BOTTOMPADDING', (0, 1), (-1, -1), 0)
#     ])
    
#     new_table_four = Table(new_table_data_four, style=new_table_style_four, colWidths=[290,290])
#     flowables.extend([new_table_four, hr_line_white])
#     #fourth section end
#     my_doc.build(flowables)
#     return pdf_buffer