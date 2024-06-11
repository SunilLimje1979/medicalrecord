from django.contrib import admin
from django.urls import path
from .views import *

from .views_pdf import * 

urlpatterns = [
    ######################### Patient Vitals  ############################  
    path("insert_patients_vitals/",insert_patients_vitals),
    path("delete_patients_vitals/",delete_patient_vitals),
    path('get_patientvitals_by_biometric_id/',get_patientvitals_by_biometric_id),
    
    ######################### Patient Prescriptions ############################  
    path("insert_prescriptions/",insert_prescriptions),
    path("delete_prescriptions/",delete_prescriptions),


    
    ######################### Patient Medication  ############################  
    path("insert_patient_medications/",insert_patient_medications),
    path("delete_patient_medications/",delete_patient_medications),
    path("get_patient_medications_byconsultationid/",get_patient_medications_byconsultationid),
    
    ######################### Patient Findings and Symtoms ############################  
    path("insert_patient_findingsandsymtoms/",insert_patient_findingsandsymtoms),
    path("delete_patient_findingsandsymtoms/",delete_patient_findingsandsymtoms),
    
    ######################### Patient Complaint  ############################  
    path("insert_patient_complaints/",insert_patient_complaints),
    path("delete_patient_complaints/",delete_patient_complaints),
    
    ######################### Patient lab investigations  ############################  
    path("insert_patient_labinvestigations/",insert_patient_labinvestigations),
    path("delete_patient_labinvestigations/",delete_patient_labinvestigations),
    path("get_labinvestigationreport_by_id/",get_labinvestigationreport_by_id),
    path("get_labinvestigation_bydoctorid/",get_labinvestigation_bydoctorid),

    ######################### Biometric ############################
     path("insert_biometric",insert_biometric,name='insert_biometric'),
     path("delete_biometric",delete_biometric,name='delete_biometric'),
     
     ######################### Consultation ############################
     path("get_all_consultation_and_prescription",get_all_consultation_and_prescription,name='get_all_consultation_and_prescription'),
     path("insert_consultation",insert_consultation,name='insert_consultation'),
     path("delete_consultation",delete_consultation,name='delete_consultation'),
     path("insert_consultations_biometrics_vitals",insert_consultations_biometrics_vitals,name='insert_consultations_biometrics_vitals'),
     path("get_consultation_byconsultationid/",get_consultation_byconsultationid,name='get_consultation_byconsultationid'),

     ##################################pdfs###############################
     path('build_pdf/', PdfCreator.as_view(), name='build_pdf'),
     path('generateprescriptionpdf/', fi_generateprescriptionpdf, name='fi_generateprescriptionpdf'),
     path('generateclinicpdf/', fi_generateclinicpdf, name='fi_generateclinicpdf'),

     path("get_patientvitals_by_appointment_id/",get_patientvitals_by_appointment_id),
     path("update_patientvitals_by_appointment_id/",update_patientvitals_by_appointment_id),

    path("get_patient_findings_symptoms_by_consultation/",get_patient_findings_symptoms_by_consultation),
    path("get_patient_labinvestigations_by_consultation_id/",get_patient_labinvestigations_by_consultation_id),
    path("update_consultation_details/",update_consultation_details),
    path("update_patient_findings_and_symptoms/",update_patient_findings_and_symptoms),
    path("get_prescription_details/",get_prescription_details),
    path("update_consultation_status/",update_consultation_status),
    path("update_prescription_details/",update_prescription_details),
    path("get_consultations_by_patient_id/",get_consultations_by_patient_id),
    path("get_consultations_by_patient_and_doctor_id/",get_consultations_by_patient_and_doctor_id),
     
]