from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from datetime import datetime
from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime
from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.http import JsonResponse
import json

from medicify_project.models import * 
from medicify_project.serializers import *
# Create your views here.

# start

######################### Patient Vitals ###################################
###################### INSERT ##################
@api_view(['POST'])
@transaction.atomic
def insert_patients_vitals(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    body = request.data

    # Validations for required fields
    required_fields = ['patient_id', 'doctor_id', 'operator_id', 'patient_status', 'patient_heart_rate', 'patient_bp_systolic', 'patient_bp_diastolic', 'patient_pain_scale', 'patient_respiratory_rate', 'patient_temperature', 'patient_chest', 'patient_ecg']
    missing_fields = [field for field in required_fields if not body.get(field)]

    if missing_fields:
        response_data['message_code'] = 999
        response_data['message_text'] = 'Failure'
        response_data['message_data'] = {f"Missing required fields: {', '.join(missing_fields)}"}
    


    else:
        # Extracting values from the request body
        patient_id = body.get('patient_id', '')
        doctor_id = body.get('doctor_id', '')
        operator_id = body.get('operator_id', '')
        patient_status = body.get('patient_status', '')
        patient_heart_rate = body.get('patient_heart_rate', '')
        patient_bp_systolic = body.get('patient_bp_systolic', '')
        patient_bp_diastolic = body.get('patient_bp_diastolic', '')
        patient_pain_scale = body.get('patient_pain_scale', '')
        patient_respiratory_rate = body.get('patient_respiratory_rate', '')
        patient_temperature = body.get('patient_temperature', '')
        patient_chest = body.get('patient_chest', '')
        patient_ecg = body.get('patient_ecg', '')
        try:
            # Validate if the patient exists
            if not Tblpatients.objects.filter(patient_id=body.get('patient_id'), isdeleted=0).exists():
                 response_data=({'message': 'Patient not found.'})
            else:
                new_vitals = Tblpatientvitals(
                            patient_id=patient_id,
                            doctor_id=doctor_id,
                            operator_id=operator_id,
                            patient_status=patient_status,
                            patient_heartratepluse=patient_heart_rate,
                            patient_bpsystolic=patient_bp_systolic,
                            patient_bpdistolic=patient_bp_diastolic,
                            patient_painscale=patient_pain_scale,
                            patient_respiratoryrate=patient_respiratory_rate,
                            patient_temparature=patient_temperature,
                            patient_chest=patient_chest,
                            patient_ecg=patient_ecg,
                            isdeleted=0
                        )

                        # Save the new instance
                new_vitals.save()

                response_data = {
                            'message_code': 1000,
                            'message_text': 'Vitals patient inserted successfully.',
                            'message_data': [{'Patient_Biometricid': new_vitals.patient_biometricid}],
                            'message_debug': debug
                        }
    

        except Exception as e:
            response_data = {'message_code': 999, 'message_text': f'Error: {str(e)}'}

    return Response(response_data, status=status.HTTP_200_OK)

###################### DELETE ##################
@api_view(['DELETE'])
def delete_patient_vitals(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': ""
    }

    # Extracting Patient_Biometricid from the request data
    patient_biometricid = request.data.get('Patient_Biometricid', '')

    if not patient_biometricid:
        response_data = {'message_code': 999, 'message_text': 'Patient biometric id is required.'}
    else:
        try:
            # Check if the patient exists
            patient_vitals = Tblpatientvitals.objects.filter(patient_biometricid=patient_biometricid, isdeleted=0).first()

            if patient_vitals:
                # Soft delete by updating IsDeleted flag
                patient_vitals.isdeleted = 1
                patient_vitals.save()

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Vitals patient deleted successfully.',
                    'message_data': [{'Patient_Biometricid': patient_biometricid}],
                    'message_debug': ""
                }
            else:
                response_data = {
                    'message_code': 999,
                    'message_text': 'Vitals patient not found.',
                    'message_data': [],
                    'message_debug': ""
                }

        except Exception as e:
            response_data = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(response_data, status=status.HTTP_200_OK)



######################### Prescription ###################################
###################### INSERT ##################
@api_view(['POST'])
def insert_prescriptions(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }

        body = request.data

        # Validation for required fields
        required_fields = ['doctor_id','patient_id','patient_status','consultation_id','prescription_datetime','prescription_details']
        missing_fields = [field for field in required_fields if not body.get(field)]

        if missing_fields:
            response_data['message_code'] = 999
            response_data['message_text'] = 'Failure'
            response_data['message_data'] = {f"Missing required fields: {', '.join(missing_fields)}"}
        else:
            # Extracting values from the request body
            doctor_id = body.get('doctor_id', '')
            patient_id = body.get('patient_id', '')
            patient_status = body.get('patient_status', '')
            consultation_id = body.get('consultation_id', '')
            prescription_datetime_str = body.get('prescription_datetime', '')
            prescription_details = body.get('prescription_details', '')

            # Convert Prescription_DateTime to epoch time
            try:
                prescription_datetime = datetime.strptime(prescription_datetime_str, '%Y-%m-%d %H:%M:%S')
                epoch_time = int(prescription_datetime.timestamp())
            except ValueError:
                response_data={'message_code': 999, 'message_text': 'Invalid datetime format.'}

            try:
                # ORM method for insertion
                prescription = Tblprescriptions(
                    doctor_id=doctor_id,
                    patient_id=patient_id,
                    patient_status=patient_status,
                    consultation_id=consultation_id,
                    prescription_datetime=epoch_time,
                    prescription_details=prescription_details,
                    isdeleted=0
                )

                # Save the new prescription instance
                prescription.save()

                # Get the last inserted ID
                last_insert_id = prescription.prescriptions_id

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Prescriptions inserted successfully.',
                    'message_data': [{'Prescriptions_Id': last_insert_id}],
                    'message_debug': debug
                }

            except Exception as e:
                response_data = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

        return Response(response_data, status=status.HTTP_200_OK)

###################### DELETE ##################
@api_view(['POST'])
def delete_prescriptions(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }

        try:
            # Extract Prescription ID from the request body
            prescriptions_id = request.data.get('Prescriptions_Id', None)

            # Check if Prescription_Id is provided
            if not prescriptions_id:
                response_data = {'message_code': 999, 'message_text': 'Prescription id is required.'}
            else:
                # Use Django ORM to get the prescription instance
                prescription = get_object_or_404(Tblprescriptions, prescriptions_id=prescriptions_id, isdeleted=0)

                # Soft delete by updating the IsDeleted flag
                prescription.isdeleted = 1
                prescription.save()

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Prescription deleted successfully.',
                    'message_data': [{'Prescriptions_Id': prescriptions_id}],
                    'message_debug': debug
                }

        except Http404:
            response_data = {'message_code': 999, 'message_text': 'Prescription not found.'}
        except Exception as e:
            response_data = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

        return Response(response_data, status=status.HTTP_200_OK)


######################### PATIENT MEDICATIONS ###################################
###################### INSERT ##################
@api_view(['POST'])
def insert_patient_medications(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }

        body = request.data
        # Validations for all fields
        required_fields = ['Doctor_Id', 'Patient_Id', 'Patient_Status', 'Consultation_Id', 'Prescription_Id',
                           'Medication_DateTime', 'Medicine_Id', 'Medicine_Form', 'Medicine_Name', 'Medicine_Duration',
                           'Medicine_Doses', 'Medicine_Dose_Interval', 'Medicine_Instruction_Id', 'Medicine_Category',
                           'Medicine_ExtraField1', 'Medicine_ExtraField2']

        missing_fields = [field for field in required_fields if not body.get(field)]

        if missing_fields:
            response_data['message_code'] = 999
            response_data['message_text'] = 'Failure'
            response_data['message_data'] = {f"Missing required fields: {', '.join(missing_fields)}"}

        # If all validations pass, proceed with insertion
        else:
            # Extracting values from the request body
            patient_id = body.get('Patient_Id', '')
            doctor_id = body.get('Doctor_Id', '')
            patient_status = body.get('Patient_Status', '')
            consultation_id = body.get('Consultation_Id', '')
            prescription_id = body.get('Prescription_Id', '')
            medication_datetime_str = body.get('Medication_DateTime', '')
            medicine_id = body.get('Medicine_Id', '')
            medicine_form = body.get('Medicine_Form', '')
            medicine_name = body.get('Medicine_Name', '')
            medicine_duration = body.get('Medicine_Duration', '')
            medicine_doses = body.get('Medicine_Doses', '')
            medicine_dose_interval = body.get('Medicine_Dose_Interval', '')
            medicine_instruction_id = body.get('Medicine_Instruction_Id', '')
            medicine_category = body.get('Medicine_Category', '')
            medicine_extra_field1 = body.get('Medicine_ExtraField1', '')
            medicine_extra_field2 = body.get('Medicine_ExtraField2', '')
            try:
                medication_datetime = datetime.strptime(medication_datetime_str, '%Y-%m-%d %H:%M:%S')
                medication_datetime_epoch = int(medication_datetime.timestamp())

                # ORM method for insertion
                medication = TblpatientMedications(
                    doctor_id=doctor_id,
                    patient_id=patient_id,
                    patient_status=patient_status,
                    consultation_id=consultation_id,
                    prescription_id=prescription_id,
                    medication_datetime=medication_datetime_epoch,
                    medicine_id=medicine_id,
                    medicine_form=medicine_form,
                    medicine_name=medicine_name,
                    medicine_duration=medicine_duration,
                    medicine_doses=medicine_doses,
                    medicine_dose_interval=medicine_dose_interval,
                    medicine_instruction_id=medicine_instruction_id,
                    medicine_category=medicine_category,
                    medicine_extrafield1=medicine_extra_field1,
                    medicine_extrafield2=medicine_extra_field2,
                    isdeleted=0
                )

                # Save the new medication instance
                medication.save()

                # Get the last inserted ID
                last_insert_id = medication.patient_medication_id

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Patient medications inserted successfully.',
                    'message_data': [{'Patient_Medication_Id': last_insert_id}],
                    'message_debug': debug
                }

            except Exception as e:
                response_data = {
                    'message_code': 999,
                    'message_text': f'Unable to insert patient medications. Error: {str(e)}',
                    'message_data': [],
                    'message_debug': debug
                }

        return Response(response_data, status=status.HTTP_200_OK)

###################### DELETE ##################
@api_view(['POST'])
def delete_patient_medications(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }

        patient_medication_id = request.data.get('Patient_Medication_Id', None)

        if not patient_medication_id:
            response_data = {'message_code': 999, 'message_text': 'Patient medication id is required.'}
        else:
            try:
                # Get the medication instance to be deleted
                medication_instance = TblpatientMedications.objects.get(patient_medication_id=patient_medication_id,isdeleted=0)

                # Soft delete by setting IsDeleted flag to True
                medication_instance.isdeleted = 1
                medication_instance.save()

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Patient medications deleted successfully.',
                    'message_data': [{'Patient_Medication_Id': patient_medication_id}],
                    'message_debug': debug
                }

            except TblpatientMedications.DoesNotExist:
                response_data = {'message_code': 999, 'message_text': 'Patient medication not found.', 'message_data': [], 'message_debug': debug}
            except Exception as e:
                response_data = {'message_code': 999, 'message_text': f'Error: {str(e)}', 'message_data': [], 'message_debug': debug}

        return Response(response_data, status=status.HTTP_200_OK)


######################### PATIENT FINDINGS AND SYMTOMS ###################################
###################### INSERT ##################
@api_view(["POST"])
def insert_patient_findingsandsymtoms(request):
    try:
        body = request.data

        # Convert date string to epoch time
        findgings_datetime_str = body.get('findgings_datetime', '')
        findgings_datetime_epoch = int(datetime.strptime(findgings_datetime_str, '%Y-%m-%d %H:%M:%S').timestamp())

        body['findgings_datetime']=findgings_datetime_epoch
        body['isdeleted']=0
        # Create serializer instance
        serializer = TblpatientFindingsandsymtomsSerializer(data=body)
        
        # Validate and save
        if serializer.is_valid():
            patientFindingsandsymtoms=serializer.save()
            response_data = {
                'message_code': 1000,
                'message_text': 'Patient findings and symptoms added successfully.',
                'message_data': {'Patient_Findings_Id': patientFindingsandsymtoms.patient_findings_id}
            }
        else:
            response_data = {
                'message_code': 999,
                'message_text': 'Validation error',
                'message_data': serializer.errors
            }

    except Exception as e:
        response_data = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(response_data,status=status.HTTP_200_OK)

###################### DELETE ##################
@api_view(["POST"])
def delete_patient_findingsandsymtoms(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }

        patient_findings_id = request.data.get('Patient_Findings_Id', None)

        if not patient_findings_id:
            response_data = {'message_code': 999, 'message_text': 'Patient findings id is required.'}
        else:
            try:
                # Get the patient findings instance
                patient_findings = TblpatientFindingsandsymtoms.objects.get(patient_findings_id=patient_findings_id, isdeleted=0)

                # Update the 'isdeleted' field
                patient_findings.isdeleted = 1
                patient_findings.save()

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Patient findings and symtoms deleted successfully.',
                    'message_data': [{'Patient_Findings_Id': patient_findings_id}],
                    'message_debug': debug
                }

            except TblpatientFindingsandsymtoms.DoesNotExist:
                response_data = {'message_code': 999, 'message_text': 'Patient findings and symtoms not found.', 'message_debug': debug}

        return Response(response_data, status=status.HTTP_200_OK)


######################### PATIENT COMPLAINTS ###################################
###################### INSERT ##################
@api_view(["POST"])
def insert_patient_complaints(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }
        # Convert complaint_datetime to epoch time
        # Convert date string to epoch time
        data=request.data
        complaint_datetime_str = data.get('complaint_datetime', '')
        complaint_datetime_epoch = int(datetime.strptime(complaint_datetime_str, '%Y-%m-%d %H:%M:%S').timestamp())
        data['complaint_datetime']=complaint_datetime_epoch
        data['isdeleted']=0
        serializer = TblpatientComplaintsSerializer(data=data)

        if serializer.is_valid():
            # Save the data using serializer
            patient_complaint = serializer.save()

            response_data = {
                'message_code': 1000,
                'message_text': 'Patient complaints information added successfully.',
                'message_data': [{'Patient_Complaint_Id': patient_complaint.patient_complaint_id}],
                'message_debug': debug
            }
        else:
            response_data['message_text'] = 'Validation error in input data.'
            response_data['message_debug'] = serializer.errors

        return Response(response_data, status=status.HTTP_200_OK)

###################### DELETE ##################
@api_view(["POST"])
def delete_patient_complaints(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }
        patient_complaint_id = request.data.get('Patient_Complaint_Id', None)

        if not patient_complaint_id:
            response_data={'message_code': 999, 'message_text': 'Patient Complaint Id is required.'}

        try:
            # Get the patient complaint instance
            patient_complaint = TblpatientComplaints.objects.get(patient_complaint_id=patient_complaint_id,isdeleted=0)

            # Soft delete by setting IsDeleted to 1
            patient_complaint.isdeleted = 1
            patient_complaint.save()

            response_data = {
                'message_code': 1000,
                'message_text': 'Patient complaint deleted successfully.',
                'message_data': {'Patient_Complaint_Id': patient_complaint_id},
                'message_debug': debug
            }

        except TblpatientComplaints.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Patient complaint not found.','message_debug': debug}

        return Response(response_data, status=status.HTTP_200_OK)


######################### PATIENT LABINVESTIGATION ###################################
###################### INSERT ##################
@api_view(['POST'])
def insert_patient_labinvestigations(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }

        # Extracting values from the request body
        body = request.data

        # Validate presence of required fields
        required_fields = ['Doctor_Id', 'Patient_Id', 'Patient_Status', 'Consultation_Id', 'Prescription_Id',
                'LabInvestigation_DateTime', 'LabInvestigation_Category', 'Patient_LabTestId',
                'Patient_LabTestReport', 'Patient_LabTestSample', 'Patient_LabTestReport_Check', 'LatTest_ExtraField1']

        missing_fields = [field for field in required_fields if not body.get(field)]

        if missing_fields:
            response_data = {
                'message_code': 999,
                'message_text': 'Failure',
                'message_data': {f"Missing required fields: {', '.join(missing_fields)}"}
            }
        else:
             # Fields taken from user
            doctor_id = body.get('Doctor_Id', '')
            patient_id = body.get('Patient_Id', '')
            patient_status = body.get('Patient_Status', '')
            consultation_id = body.get('Consultation_Id', '')
            prescription_id = body.get('Prescription_Id', '')
            lab_investigation_datetime = body.get('LabInvestigation_DateTime', '')
            lab_investigation_category = body.get('LabInvestigation_Category', '')
            patient_labtest_id = body.get('Patient_LabTestId', '')
            patient_labtest_report = body.get('Patient_LabTestReport', '')
            patient_labtest_sample = body.get('Patient_LabTestSample', '')
            patient_labtest_report_check = body.get('Patient_LabTestReport_Check', '')
            lat_test_extra_field1 = body.get('LatTest_ExtraField1', '')
            try:
                # Convert LabInvestigation_DateTime to epoch time
                lab_investigation_datetime_epoch = int(
                    datetime.strptime(lab_investigation_datetime, "%Y-%m-%d %H:%M:%S").timestamp()
                )

                # ORM method for insertion
                lab_investigation = TblpatientLabinvestigations(
                    doctor_id=doctor_id,
                    patient_id=patient_id,
                    patient_status=patient_status,
                    consultation_id=consultation_id,
                    prescription_id=prescription_id,
                    labinvestigation_datetime=lab_investigation_datetime_epoch,
                    labinvestigation_category=lab_investigation_category,
                    patient_labtestid=patient_labtest_id,
                    patient_labtestreport=patient_labtest_report,
                    patient_labtestsample=patient_labtest_sample,
                    patient_labtestreport_check=patient_labtest_report_check,
                    lattest_extrafield1=lat_test_extra_field1,
                    isdeleted=0
                )

                # Save the new lab_investigation instance
                lab_investigation.save()

                # Get the last inserted ID
                last_insert_id = lab_investigation.patient_labinvestigation_id

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Patient lab investigations inserted successfully.',
                    'message_data': [{'Patient_LabInvestigation_Id': last_insert_id}],
                    'message_debug': debug
                }

            except Exception as e:
                response_data = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

        return Response(response_data, status=status.HTTP_200_OK)

###################### DELETE ##################
@api_view(['POST'])
def delete_patient_labinvestigations(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }

        patient_lab_investigation_id = request.data.get('Patient_LabInvestigation_Id', '')

        if not patient_lab_investigation_id:
            response_data = {'message_code': 999, 'message_text': 'Patient lab investigation id is required.'}
        else:
            try:
                # Fetch the instance using the provided ID
                lab_investigation_instance = TblpatientLabinvestigations.objects.get(patient_labinvestigation_id=patient_lab_investigation_id,isdeleted=0)

                # Set IsDeleted to 1
                lab_investigation_instance.isdeleted = 1

                # Save the changes
                lab_investigation_instance.save()

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Patient lab investigations deleted successfully.',
                    'message_data': [{'Patient_LabInvestigation_Id': patient_lab_investigation_id}],
                    'message_debug': debug
                }

            except TblpatientLabinvestigations.DoesNotExist:
                response_data = {'message_code': 999, 'message_text': 'Lab investigation not found.'}

            except Exception as e:
                response_data = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

        return Response(response_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def insert_biometric(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}

    patient_id = request.data.get('Patient_Id', '')
    doctor_id = request.data.get('Doctor_Id', '')
    operator_id = request.data.get('Operator_Id', '')
    patient_status = request.data.get('Patient_Status', '')
    patient_height = request.data.get('Patient_Height', '')
    patient_weight = request.data.get('Patient_Weight', '')
    patient_bmi = request.data.get('Patient_BMI', '')

    if not patient_id:
            res = {'message_code': 999, 'message_text': 'Patient id is required.'}
    else:
        patient_count = Tblpatients.objects.filter(isdeleted=0, patient_id=patient_id).count()
        print(patient_count)
        if patient_count >= 1:
            if not doctor_id:
                res = {'message_code': 999, 'message_text': 'Doctor id is required.'}
            elif not patient_status:
                res = {'message_code': 999, 'message_text': 'Patient status is required.'}
            else:
                # Insert into tblPatientBiometrics
                try:
                        patient_biometrics = Tblpatientbiometrics.objects.create(
                            patient_id=patient_id,
                            doctor_id=doctor_id,
                            operator_id=operator_id,
                            patient_status=patient_status,
                            patient_height=patient_height,
                            patient_weight=patient_weight,
                            patient_bmi=patient_bmi,
                            isdeleted=0
                        )

                        if patient_biometrics:
                            res = {
                                'message_code': 1000,
                                'message_text': 'Patient biometrics information inserted successfully.',
                                'message_data': [{'Patient_Biometricid': patient_biometrics.patient_biometricid}],
                                'message_debug': []  # Empty debug array as in your PHP code
                            }
                        else:
                            res = {
                                'message_code': 999,
                                'message_text': 'Unable to insert patient biometrics.',
                                'message_data': [],
                                'message_debug': []  # Empty debug array as in your PHP code
                            }
                except Exception as e:
                    res = {'message_code': 999, 'message_text': f'Unable to insert Medicine instructions. Error: {str(e)}',
                        'message_data': [],
                        'message_debug': [] if debug == "" else [{'Debug': debug}]}            
        else:
            res = {
                'message_code': 999,
                'message_text': 'Patient Id not in patients. Please try another.',
                'message_data': [],
                'message_debug': [] if debug == "" else [{'Debug': debug}]
                } 
    return Response(res, status=status.HTTP_200_OK)



@api_view(['POST'])
def delete_biometric(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    
    patient_biometric_id = request.data.get('Patient_Biometricid', '')

    if not patient_biometric_id:
        res = {'message_code': 999, 'message_text': 'Patient biometric id is required.'}
    else:
        try:
            if Tblpatientbiometrics.objects.filter(patient_biometricid=patient_biometric_id).exists():
                patient_biometric = Tblpatientbiometrics.objects.get(patient_biometricid=patient_biometric_id)
                patient_biometric.isdeleted = 1
                patient_biometric.save()
                
                res = {
                        'message_code': 1000,
                        'message_text': "Biometric deleted successfully.",
                        'message_data': [{'patient_biometric_id': patient_biometric_id}],
                        'message_debug': [{"Debug": debug}] if debug != "" else []
                    }
            else:
                res = {
                    'message_code': 999,
                    'message_text': "Biometric id not found.",
                    'message_data': [],
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }

        except Exception as e:
            res = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(res, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_all_consultation_and_prescription(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    patient_id = request.data.get('Patient_Id', '')
    doctor_id = request.data.get('Doctor_Id', '')
    

    if not patient_id:
        res = {'message_code': 999, 'message_text': 'Patient id is required.'}
    elif not doctor_id:
        res = {'message_code': 999, 'message_text': 'Doctor id is required.'}
    else:    
        try:
           

            consultation = Tblconsultations.objects.filter(
                Q(patient_id=patient_id, doctor_id=doctor_id, isdeleted=0)
            )

            resArray = []

            for result in consultation:
                consultation_data = ConsultationSerializer(result).data

                prescriptions = Tblprescriptions.objects.filter(
                    Q(consultation_id=result.consultation_id, isdeleted=0)
                )
                prescriptions_data = PrescriptionsSerializer(prescriptions, many=True).data

                findingsandsymtoms = TblpatientFindingsandsymtoms.objects.filter(
                    Q(consultation_id=result.consultation_id, isdeleted=0)
                )
                findingsandsymtoms_data = FindingsandsymtomsSerializer(findingsandsymtoms, many=True).data

                medications = TblpatientMedications.objects.filter(
                    Q(consultation_id=result.consultation_id, isdeleted=0)
                )
                medications_data = MedicationsSerializer(medications, many=True).data

                labinvestigations = TblpatientLabinvestigations.objects.filter(
                    Q(consultation_id=result.consultation_id, isdeleted=0)
                )
                labinvestigations_data = LabinvestigationsSerializer(labinvestigations, many=True).data

                combined_data = {
                    **consultation_data,
                    "Prescriptions": prescriptions_data,
                    "Findingsandsymtoms": findingsandsymtoms_data,
                    "Medications": medications_data,
                    "Labinvestigations": labinvestigations_data,
                }

                resArray.append(combined_data)

            if resArray:
                            res = {
                                'message_code': 1000,
                                'message_text': 'Patient information for this Patient id,Doctor id from consultation,prescriptions,findingsandsymtoms,Medications and lab investigations retrived successfully.',
                                'message_data': [{'result': resArray}],
                                'message_debug': []  # Empty debug array as in your PHP code
                            }
            else:
                            res = {
                                'message_code': 999,
                                'message_text': 'Unable to get patient information.',
                                'message_data': [],
                                'message_debug': []  # Empty debug array as in your PHP code
                            }
        except Exception as e:
                res = {'message_code': 999, 'message_text': f'Unable to get patient information. Error: {str(e)}',
                    'message_data': [],
                    'message_debug': [] if debug == "" else [{'Debug': debug}]}            
    
    return Response(res, status=status.HTTP_200_OK)


@api_view(['POST'])
def insert_consultation(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
     
    patient_id = request.data.get('Patient_Id')
    doctor_id = request.data.get('Doctor_Id')
    patient_status = request.data.get('Patient_Status')
    consultation_datetime = request.data.get('Consultation_DateTime')
    consultation_mode = request.data.get('Consultation_Mode', 1)
    visit_reason = request.data.get('Visit_Reason', '')
    consultation_duration = request.data.get('Consultation_Duration', 0)
    further_assisted = request.data.get('Further_Assited', 0)
    followup_datetime = request.data.get('Followup_DateTime', 0)
    instructions = request.data.get('instructions')
    consultation_fees = request.data.get('consultation_fees')
    referred_to_doctor = request.data.get('referred_to_doctor')


    # Validate appointment_id
    if not doctor_id:
        res = {'message_code': 999, 'message_text': 'Doctor id is required.'}
    elif not patient_id:
        res = {'message_code': 999, 'message_text': 'Patient id is required.'}
    elif not patient_status:
        res = {'message_code': 999, 'message_text': 'Patient status is required.'}
    elif not consultation_datetime:
        res = {'message_code': 999, 'message_text': 'Consultation date time is required.'}
    else:
        # print(doctor_id)
        try:
            
            consultation = Tblconsultations.objects.create(
                doctor_id_id=doctor_id,
                patient_id_id=patient_id,
                patient_status=patient_status,
                consultation_datetime=consultation_datetime,
                consultation_mode=consultation_mode,
                visit_reason=visit_reason,
                consultation_duration=consultation_duration,
                further_assited=further_assisted,
                followup_datetime=followup_datetime,
                isdeleted=0,
                instructions=instructions,
                consultation_fees=consultation_fees,
                referred_to_doctor=referred_to_doctor
            )

            res = {
                'message_code': 1000,
                'message_text': 'Consultation insert successfully',
                'message_data':{'consultation_id': str(consultation.consultation_id)},
                'message_debug': [{"Debug": debug}] if debug != "" else []
            }

        except Tblconsultations.DoesNotExist:
            res = {'message_code': 999, 'message_text': 'Consultation not found'}

        except Exception as e:
            res = {'message_code': 999, 'message_text': f'Error: {str(e)}'}

    return Response(res, status=status.HTTP_200_OK)


@api_view(['POST'])
def delete_consultation(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    
    consultation_id = request.data.get('Consultation_Id', '')

    if not consultation_id:
        res = {'message_code': 999, 'message_text': 'Consultation id is required.'}
    else:
        try:
            if Tblconsultations.objects.filter(consultation_id=consultation_id).exists():
                consultation = Tblconsultations.objects.get(consultation_id=consultation_id)
                consultation.isdeleted = 1
                consultation.save()
                
                res = {
                        'message_code': 1000,
                        'message_text': "Consultations deleted successfully.",
                        'message_data': [{'consultation_id': consultation_id}],
                        'message_debug': [{"Debug": debug}] if debug != "" else []
                    }
            else:
                res = {
                    'message_code': 999,
                    'message_text': "Consultations id not found.",
                    'message_data': [],
                    'message_debug': [{"Debug": debug}] if debug != "" else []
                }

        except Exception as e:
            res = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

    return Response(res, status=status.HTTP_200_OK)


@api_view(['POST'])
def insert_consultations_biometrics_vitals(request):
    debug = ""
    res = {'message_code': 999, 'message_text': 'Functional part is commented.', 'message_data': [], 'message_debug': debug}
    
    patient_id = request.data.get('Patient_Id', '')
    doctor_id = request.data.get('Doctor_Id', '')
    patient_status = request.data.get('Patient_Status', '')
    consultation_datetime = request.data.get('Consultation_DateTime', '')
    consultation_mode = request.data.get('Consultation_Mode', 1)
    visit_reason = request.data.get('Visit_Reason', '')
    consultation_duration = request.data.get('Consultation_Duration', 0)
    further_assisted = request.data.get('Further_Assited', 0)
    followup_datetime = request.data.get('Followup_DateTime', 0)
    instructions = request.data.get('instructions')
    consultation_fees = request.data.get('consultation_fees')
    referred_to_doctor = request.data.get('referred_to_doctor')
    further_assited = request.data.get('further_assited')

    # tblPatientBiometrics
    operator_id = request.data.get('Operator_Id', 0)
    patient_height = request.data.get('Patient_Height', 0)
    patient_weight = request.data.get('Patient_Weight', 0)
    patient_bmi = request.data.get('Patient_BMI', 0)

    # tblPatientVitals
    heart_rate_pulse = request.data.get('Patient_HeartRatePluse', '')
    bp_systolic = request.data.get('Patient_BPSystolic', '')
    bp_diastolic = request.data.get('Patient_BPDistolic', '')
    pain_scale = request.data.get('Patient_PainScale', '')
    respiratory_rate = request.data.get('Patient_RespiratoryRate', '')
    temperature = request.data.get('Patient_Temparature', '')
    chest = request.data.get('Patient_Chest', '')
    ecg = request.data.get('Patient_ECG', '')

    # All validations and separate message for each failed condition
    if not doctor_id:
        res = {'message_code': 999, 'message_text': 'Doctor id is required.'}
    elif not patient_id:
        res = {'message_code': 999, 'message_text': 'Patient id is required.'}
    elif not patient_status:
        res = {'message_code': 999, 'message_text': 'Patient status is required.'}
    elif not consultation_datetime:
        res = {'message_code': 999, 'message_text': 'Consultation date time is required.'}
    elif not heart_rate_pulse:
        res = {'message_code': 999, 'message_text': 'Patient heart rate pulse is required.'}
    elif not bp_systolic:
        res = {'message_code': 999, 'message_text': 'Patient BP Systolic is required.'}
    elif not bp_diastolic:
        res = {'message_code': 999, 'message_text': 'Patient BP Diastolic is required.'}
    elif not pain_scale:
        res = {'message_code': 999, 'message_text': 'Patient pain scale is required.'}
    elif not respiratory_rate:
        res = {'message_code': 999, 'message_text': 'Patient respiratory rate is required.'}
    elif not temperature:
        res = {'message_code': 999, 'message_text': 'Patient temperature is required.'}
    elif not chest:
        res = {'message_code': 999, 'message_text': 'Patient chest is required.'}
    elif not ecg:
        res = {'message_code': 999, 'message_text': 'Patient ECG is required.'}
    else:
        try:
           
            Consultationdata = {
                'doctor_id': doctor_id,
                'patient_id': patient_id,
                'patient_status': patient_status,
                'consultation_datetime': consultation_datetime,
                'consultation_mode': consultation_mode,
                'visit_reason': visit_reason,
                'consultation_duration': consultation_duration,
                'further_assisted': further_assisted,
                'followup_datetime': followup_datetime,
                'isdeleted': 0,
                'instructions': instructions,
                'consultation_fees': consultation_fees,
                'referred_to_doctor': referred_to_doctor,
                'further_assited':further_assited
            }
            Consultationserializer = ConsultationSerializer(data=Consultationdata)
            if Consultationserializer.is_valid():
                instance = Consultationserializer.save()
                last_consultation_id = instance.consultation_id
                
                if(last_consultation_id):
                    Patientdata = {
                        'patient_id': patient_id,
                        'doctor_id': doctor_id,
                        'consultation_id': last_consultation_id,
                        'operator_id': operator_id,
                        'patient_status': patient_status,
                        'patient_height': patient_height,
                        'patient_weight': patient_weight,
                        'patient_bmi': patient_bmi,
                        'isdeleted': 0
                    }
                    PatientBiometrics = PatientBiometricsSerializer(data=Patientdata)
                    if PatientBiometrics.is_valid():
                        instance = PatientBiometrics.save()
                        lastBiometricId = instance.patient_biometricid
                        
                        patientvitalsdata={
                            'patient_id': patient_id,
                            'doctor_id': doctor_id,
                            'consultation_id': last_consultation_id,
                            'operator_id': operator_id,
                            'patient_status': patient_status,
                            'patient_heartratepluse': heart_rate_pulse,
                            'patient_bpsystolic': bp_systolic,
                            'patient_bpdistolic': bp_diastolic,
                            'patient_painscale': pain_scale,
                            'patient_respiratoryrate': respiratory_rate,
                            'patient_temparature': temperature,
                            'patient_chest': chest,
                            'patient_ecg': ecg,
                            'isdeleted': 0
                        }
                        patientvitals = TblPatientVitalsSerializer(data=patientvitalsdata)
                        if patientvitals.is_valid():
                            instance = patientvitals.save()
                            lastpatient_biometricid = instance.patient_biometricid
                            res = {
                                'message_code': 1000,
                                'message_text': 'Success',
                                'message_data': [{
                                          'Consultation_Id': last_consultation_id,
                                          'Patient_Biometricid': lastBiometricId,
                                          'vitals_id': lastpatient_biometricid}],
                                'message_debug': debug if debug else []
                            }
                        else:
                            res = {
                                'message_code': 2000,
                                'message_text': 'Validation Error',
                                'message_errors': patientvitals.errors
                            }                 
                         

                    else:
                        res = {
                            'message_code': 2000,
                            'message_text': 'Validation Error',
                            'message_errors': PatientBiometrics.errors
                        }
            else:
                    res = {
                        'message_code': 2000,
                        'message_text': 'Validation Error',
                        'message_errors': Consultationserializer.errors
                    }

        except Exception as e:
            res = {'message_code': 999, 'message_text': f'Error: {str(e)}'}

    return Response(res, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_patientvitals_by_biometric_id(request):
        debug = []
        response_data = {
            'message_code': 999,
            'message_text': 'Functional part is commented.',
            'message_data': [],
            'message_debug': debug
        }
        patient_biometric_id = request.data.get('patient_biometric_id', None)

        if not patient_biometric_id:
            response_data={'message_code': 999, 'message_text': 'patient biometric Id is required.'}
        
        else:
            try:
                # Get the patient complaint instance
                patientvital = Tblpatientvitals.objects.get(patient_biometricid=patient_biometric_id)
                serializer = TblPatientVitalsSerializer(patientvital)
                result = serializer.data
                    
                response_data = {
                        'message_code': 1000,
                        'message_text': 'Appointment details are fetched successfully',
                        'message_data': result,
                        'message_debug': debug
                    }

            except Tblpatientvitals.DoesNotExist:
                response_data = {'message_code': 999, 'message_text': 'Patient vitals not found.','message_debug': debug}

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_labinvestigationreport_by_id(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    lab_investigation_id = request.data.get('lab_investigation_id',None)

    if lab_investigation_id is not None:
        try:
            lab_investigation = TblpatientLabinvestigations.objects.get(patient_labinvestigation_id=lab_investigation_id)
            serializer = LabInvestigationSerializer(lab_investigation)
            result = serializer.data

            response_data = {
                'message_code': 1000,
                'message_text': 'Lab investigation details fetched successfully',
                'message_data': result,
                'message_debug': debug
            }

        except TblpatientLabinvestigations.DoesNotExist:
            response_data = {'message_code': 404, 'message_text': 'Lab investigation not found', 'message_debug': debug}

    else:
        response_data = {'message_code': 400, 'message_text': 'Lab investigation id is required', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


# end