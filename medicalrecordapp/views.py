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
def insert_patients_vitals(request):
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': []
    }

    serializer = TblPatientVitalsSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        response_data = {
            'message_code': 1000,
            'message_text': 'Vitals patient inserted successfully.',
            'message_data': [{'Patient_Biometricid': serializer.data['patient_biometricid']}],
            'message_debug': []
        }
    else:
        response_data['message_data'] = serializer.errors

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
                
                prescription = {
                    'doctor_id':doctor_id,
                    'patient_id':patient_id,
                    'patient_status':patient_status,
                    'consultation_id':consultation_id,
                    'prescription_datetime':epoch_time,
                    'prescription_details':prescription_details,
                    'isdeleted':0
                }
                prescriptionSerializer = PrescriptionsSerializer(data=prescription)
                if prescriptionSerializer.is_valid():
                    instance = prescriptionSerializer.save()
                    last_insert_id = instance.prescriptions_id

                    response_data = {
                    'message_code': 1000,
                    'message_text': 'Prescriptions inserted successfully.',
                    'message_data': [{'Prescriptions_Id': last_insert_id}],
                    'message_debug': debug
                }
                else:
                    response_data = {
                        'message_code': 2000,
                        'message_text': 'Validation Error',
                        'message_errors': prescriptionSerializer.errors
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

    data = request.data
    # Convert Medication_DateTime to epoch time
    medication_datetime_str = data.get('medication_datetime', '')
    try:
        medication_datetime = datetime.strptime(medication_datetime_str, '%Y-%m-%d %H:%M:%S')
        data['medication_datetime'] = int(medication_datetime.timestamp())
    except ValueError:
        response_data = {
            'message_code': 999,
            'message_text': 'Invalid datetime format.',
            'message_data': [],
            'message_debug': debug
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    serializer = PatientMedicationsSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        response_data = {
            'message_code': 1000,
            'message_text': 'Patient medications inserted successfully.',
            'message_data': [{'Patient_Medication_Id': serializer.data['patient_medication_id']}],
            'message_debug': debug
        }
    else:
        response_data = {
            'message_code': 999,
            'message_text': 'Validation Error',
            'message_data': serializer.errors
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
# @api_view(['POST'])
# def insert_patient_labinvestigations(request):
#         debug = []
#         response_data = {
#             'message_code': 999,
#             'message_text': 'Functional part is commented.',
#             'message_data': [],
#             'message_debug': debug
#         }

#         # Extracting values from the request body
#         body = request.data

#         # Validate presence of required fields
#         required_fields = ['Doctor_Id', 'Patient_Id', 'Patient_Status', 'Consultation_Id', 'Prescription_Id',
#                 'LabInvestigation_DateTime', 'LabInvestigation_Category', 'Patient_LabTestId',
#                 'Patient_LabTestReport', 'Patient_LabTestSample', 'Patient_LabTestReport_Check', 'LatTest_ExtraField1']

#         missing_fields = [field for field in required_fields if not body.get(field)]

#         if missing_fields:
#             response_data = {
#                 'message_code': 999,
#                 'message_text': 'Failure',
#                 'message_data': {f"Missing required fields: {', '.join(missing_fields)}"}
#             }
#         else:
#              # Fields taken from user
#             doctor_id = body.get('Doctor_Id', '')
#             patient_id = body.get('Patient_Id', '')
#             patient_status = body.get('Patient_Status', '')
#             consultation_id = body.get('Consultation_Id', '')
#             prescription_id = body.get('Prescription_Id', '')
#             lab_investigation_datetime = body.get('LabInvestigation_DateTime', '')
#             lab_investigation_category = body.get('LabInvestigation_Category', '')
#             patient_labtest_id = body.get('Patient_LabTestId', '')
#             patient_labtest_report = body.get('Patient_LabTestReport', '')
#             patient_labtest_sample = body.get('Patient_LabTestSample', '')
#             patient_labtest_report_check = body.get('Patient_LabTestReport_Check', '')
#             lat_test_extra_field1 = body.get('LatTest_ExtraField1', '')
#             try:
#                 # Convert LabInvestigation_DateTime to epoch time
#                 lab_investigation_datetime_epoch = int(
#                     datetime.strptime(lab_investigation_datetime, "%Y-%m-%d %H:%M:%S").timestamp()
#                 )

#                 lab_investigation = {
#                     'doctor_id':doctor_id,
#                     'patient_id':patient_id,
#                     'patient_status':patient_status,
#                     'consultation_id':consultation_id,
#                     'prescription_id':prescription_id,
#                     'labinvestigation_datetime':lab_investigation_datetime_epoch,
#                     'labinvestigation_category':lab_investigation_category,
#                     'patient_labtestid':patient_labtest_id,
#                     'patient_labtestreport':patient_labtest_report,
#                     'patient_labtestsample':patient_labtest_sample,
#                     'patient_labtestreport_check':patient_labtest_report_check,
#                     'lattest_extrafield1':lat_test_extra_field1,
#                     'isdeleted':0
#                 }
#                 lab_investigationSerializer = LabInvestigationSerializer(data=lab_investigation)
#                 if lab_investigationSerializer.is_valid():
#                     instance = lab_investigationSerializer.save()
#                     last_insert_id = instance.patient_labinvestigation_id

#                     response_data = {
#                     'message_code': 1000,
#                     'message_text': 'Patient lab investigations inserted successfully.',
#                     'message_data': [{'Patient_LabInvestigation_Id': last_insert_id}],
#                     'message_debug': debug
#                 }
#                 else:
#                     response_data = {
#                         'message_code': 2000,
#                         'message_text': 'Validation Error',
#                         'message_errors': lab_investigationSerializer.errors
#                     }

               

#             except Exception as e:
#                 response_data = {'message_code': 999, 'message_text': f"Error: {str(e)}"}

#         return Response(response_data, status=status.HTTP_200_OK)
@api_view(['POST'])
def insert_patient_labinvestigations(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    # Extract the labinvestigation_datetime from the request data
    labinvestigation_datetime_str = request.data.get('labinvestigation_datetime', '')

    # Convert labinvestigation_datetime to epoch time
    try:
        labinvestigation_datetime = datetime.strptime(labinvestigation_datetime_str, '%Y-%m-%d %H:%M:%S')
        epoch_time = int(labinvestigation_datetime.timestamp())
    except ValueError:
        response_data = {'message_code': 999, 'message_text': 'Invalid datetime format.'}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    # Add the converted epoch time back to the request data
    request.data['labinvestigation_datetime'] = epoch_time

    # Use the serializer with the modified data
    serializer = LabInvestigationSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        response_data = {
            'message_code': 1000,
            'message_text': 'Patient lab investigations inserted successfully.',
            'message_data': [{'Patient_LabInvestigation_Id': serializer.data['patient_labinvestigation_id']}],
            'message_debug': debug
        }
    else:
        response_data = {
            'message_code': 999,
            'message_text': 'Validation Error',
            'message_data': serializer.errors
        }

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
    consultation_datetime_str = request.data.get('Consultation_DateTime')
    consultation_datetime_epoch = datetime.strptime(consultation_datetime_str, '%Y-%m-%d %H:%M:%S')
    consultation_datetime = int(consultation_datetime_epoch.timestamp())
    print(consultation_datetime)
    consultation_mode = request.data.get('Consultation_Mode', 1)
    visit_reason = request.data.get('Visit_Reason', '')
    consultation_duration = request.data.get('Consultation_Duration', 0)
    further_assisted = request.data.get('Further_Assited', 0)
    followup_datetime_str = request.data.get('Followup_DateTime', 0)
    
    followup_datetime_epoch = datetime.strptime(followup_datetime_str, '%Y-%m-%d %H:%M:%S')
    followup_datetime = int(followup_datetime_epoch.timestamp())
    instructions = request.data.get('instructions')
    consultation_fees = request.data.get('consultation_fees')
    referred_to_doctor = request.data.get('referred_to_doctor')
    referred_by_doctor = request.data.get('referred_by_doctor')
    appointment_id = request.data.get('appointment_id',"")
    consultation_status = request.data.get('consultation_status',"")
    

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
                referred_to_doctor=referred_to_doctor,
                referred_by_doctor = referred_by_doctor,
                appointment_id=appointment_id,
                consultation_status=consultation_status
            )
            data = {}
            consultation_id = consultation.consultation_id
            data['consultation_id'] = consultation_id

            if consultation_id:
                appointment = Tbldoctorappointments.objects.filter(appointment_id=appointment_id)
                serializer = TbldoctorappointmentsSerializer(appointment, many=True)
                result = serializer.data

                if result:  # Check if the result list is not empty
                    appointment_id = result[0]['appointment_id']

                    if appointment_id:
                        appointment_queryset = Tbldoctorappointments.objects.get(appointment_id=appointment_id)
                        serializer = TbldoctorappointmentsSerializer(appointment_queryset, data=data, partial=True)
                        if serializer.is_valid():
                            updated_data = serializer.validated_data  # Get the validated data after a successful update
                            serializer.save()
                            
            
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
    consultation_datetime_str = request.data.get('Consultation_DateTime')
    consultation_datetime_epoch = datetime.strptime(consultation_datetime_str, '%Y-%m-%d %H:%M:%S')
    consultation_datetime = int(consultation_datetime_epoch.timestamp())
    consultation_mode = request.data.get('Consultation_Mode', 1)
    visit_reason = request.data.get('Visit_Reason', '')
    consultation_duration = request.data.get('Consultation_Duration', 0)
    further_assisted = request.data.get('Further_Assited', 0)
    followup_datetime_str = request.data.get('Followup_DateTime', 0)
    
    followup_datetime_epoch = datetime.strptime(followup_datetime_str, '%Y-%m-%d %H:%M:%S')
    
    followup_datetime = int(followup_datetime_epoch.timestamp())
    instructions = request.data.get('instructions')
    consultation_fees = request.data.get('consultation_fees')
    referred_to_doctor = request.data.get('referred_to_doctor')
    further_assited = request.data.get('further_assited')
    referred_by_doctor = request.data.get('referred_to_doctor')
    appointment_id = request.data.get('appointment_id',"")

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
    weight = request.data.get('weight', '')

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
                'further_assited':further_assited,
                'referred_by_doctor':referred_by_doctor,
                'appointment_id':appointment_id
            }
            Consultationserializer = ConsultationSerializer(data=Consultationdata)
            if Consultationserializer.is_valid():
                instance = Consultationserializer.save()
                last_consultation_id = instance.consultation_id
                
                if(last_consultation_id):

                    data = {}
                    consultation_id = last_consultation_id
                    data['consultation_id'] = consultation_id

                    if consultation_id:
                        appointment = Tbldoctorappointments.objects.filter(appointment_id=appointment_id)
                        serializer = TbldoctorappointmentsSerializer(appointment, many=True)
                        result = serializer.data

                        if result:  # Check if the result list is not empty
                            appointment_id = result[0]['appointment_id']

                            if appointment_id:
                                appointment_queryset = Tbldoctorappointments.objects.get(appointment_id=appointment_id)
                                serializer = TbldoctorappointmentsSerializer(appointment_queryset, data=data, partial=True)
                                if serializer.is_valid():
                                    updated_data = serializer.validated_data  # Get the validated data after a successful update
                                    serializer.save()

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
                            'isdeleted': 0,
                            'weight':weight
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
                patientvital = Tblpatientvitals.objects.filter(patient_biometricid=patient_biometric_id)
                serializer = TblPatientVitalsSerializer(patientvital, many=True)
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
            serializer = LabInvestigationSerializer(lab_investigation, many=True)
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


@api_view(["POST"])
def get_labinvestigation_bydoctorid(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    doctor_id = request.data.get('doctor_id',None)

    if doctor_id is not None:
        try:
            lab_investigation = Tbllabinvestigations.objects.filter(doctor_id=doctor_id,isdeleted=0)
            serializer = TbllabinvestigationsSerializer(lab_investigation, many=True)
            result = serializer.data

            response_data = {
                'message_code': 1000,
                'message_text': 'Lab investigation details by doctor id fetched successfully',
                'message_data': result,
                'message_debug': debug
            }

        except Tbllabinvestigations.DoesNotExist:
            response_data = {'message_code': 404, 'message_text': 'Lab investigation not found', 'message_debug': debug}

    else:
        response_data = {'message_code': 400, 'message_text': 'Doctor id is required', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(["POST"])
def get_consultation_byconsultationid(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    consultation_id = request.data.get('consultation_id',None)

    if consultation_id is not None:
        try:
            consultation_queryset = Tblconsultations.objects.filter(consultation_id=consultation_id)
            serializer = ConsultationSerializer(consultation_queryset, many=True)
            result = serializer.data

            response_data = {
                'message_code': 1000,
                'message_text': 'consultations details fetched successfully',
                'message_data': result,
                'message_debug': debug
            }

        except Tblconsultations.DoesNotExist:
            response_data = {'message_code': 404, 'message_text': 'Tblconsultations not found', 'message_debug': debug}

    else:
        response_data = {'message_code': 400, 'message_text': 'consultation id is required', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_patient_medications_byconsultationid(request):
    debug = ""
    res = {'message_code': 999, 'message_text': "Failure", 'message_data': {'Functional part is commented.'}, 'message_debug': debug}

    try:
        if request.method == 'POST':
            data = request.data

            consultation_id = request.data.get('consultation_id',None)
            if not consultation_id:
                return Response({'message_code': 999, 'message_text': 'consultation id is required.'})

            try:
                # Fetching the existing TbldoctorMedicines instance from the database
                patient_medications = TblpatientMedications.objects.filter(consultation_id=consultation_id,isdeleted=0)
                serializer = MedicationsSerializer(patient_medications, many=True)

                if(serializer):
                    res = {
                        'message_code': 1000,
                        'message_text': 'patient medications retrived successfully.',
                        'message_data': serializer.data,
                        'message_debug': debug
                    }
                else:
                    res = {
                        'message_code': 2000,
                        'message_text': 'Validation Error',
                        'message_errors': patient_medications.errors
                    }

            except TblpatientMedications.DoesNotExist:
                return Response({
                    'message_code': 999,
                    'message_text': f'patient medications with consultation id {consultation_id} not found.',
                    'message_data': { },
                    'message_debug': debug if debug else []
                }, status=status.HTTP_200_OK)
    except Exception as e:
        res = {
            'message_code': 999,
            'message_text': f'Error in get_patient_medications_byconsultationid. Error: {str(e)}',
            'message_data': {},
            'message_debug': debug if debug else []
        }

    return Response(res, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_patientvitals_by_appointment_id(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': None,
        'message_debug': debug
    }
    appointment_id = request.data.get('appointment_id', None)

    if not appointment_id:
        response_data = {'message_code': 999, 'message_text': 'Appointment ID is required.'}
    else:
        try:
            # Get the patient vitals instance based on the appointment ID
            patientvitals = Tblpatientvitals.objects.get(appointment_id=appointment_id)
            serializer = TblPatientVitalsSerializer(patientvitals)
            result = serializer.data

            response_data = {
                'message_code': 1000,
                'message_text': 'Patient vitals fetched successfully',
                'message_data': result,
                'message_debug': debug
            }

        except Tblpatientvitals.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Patient vitals not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_patientvitals_by_appointment_id(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': None,
        'message_debug': debug
    }
    appointment_id = request.data.get('appointment_id', None)

    if not appointment_id:
        response_data = {'message_code': 999, 'message_text': 'Appointment ID is required.'}
    else:
        try:
            # Get the patient vitals instance based on the appointment ID
            patientvitals = Tblpatientvitals.objects.get(appointment_id=appointment_id)
            serializer = TblPatientVitalsSerializer(patientvitals, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'message_code': 1000,
                    'message_text': 'Patient vitals updated successfully',
                    'message_data': serializer.data,
                    'message_debug': debug
                }
            else:
                response_data = {'message_code': 999, 'message_text': 'Invalid data provided.', 'message_debug': debug}

        except Tblpatientvitals.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Patient vitals not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(["POST"])
def get_patient_findings_symptoms_by_consultation(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    consultation_id = request.data.get('consultation_id', None)

    if not consultation_id:
        response_data = {'message_code': 999, 'message_text': 'Consultation ID is required.'}
    else:
        try:
            findings_symptoms = TblpatientFindingsandsymtoms.objects.filter(consultation_id=consultation_id)
            serializer = TblpatientFindingsandsymtomsSerializer(findings_symptoms, many=True)
            response_data = {
                'message_code': 1000,
                'message_text': 'Patient findings and symptoms fetched successfully.',
                'message_data': serializer.data,
                'message_debug': debug
            }
        except TblpatientFindingsandsymtoms.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Patient findings and symptoms not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_patient_labinvestigations_by_consultation_id(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    consultation_id = request.data.get('consultation_id', None)

    if not consultation_id:
        response_data = {'message_code': 999, 'message_text': 'Consultation ID is required.'}
    else:
        try:
            labinvestigations = TblpatientLabinvestigations.objects.filter(consultation_id=consultation_id,isdeleted=0)
            serializer = LabInvestigationSerializer(labinvestigations, many=True)
            response_data = {
                'message_code': 1000,
                'message_text': 'Patient lab investigations details fetched successfully.',
                'message_data': serializer.data,
                'message_debug': debug
            }
        except TblpatientLabinvestigations.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Patient lab investigations not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(["POST"])
def get_prescription_details(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    consultation_id = request.data.get('consultation_id', None)

    if not consultation_id:
        response_data = {'message_code': 999, 'message_text': 'Consultation ID is required.'}
    else:
        try:
            prescriptions = Tblprescriptions.objects.filter(consultation_id=consultation_id)
            serializer = TblPrescriptionsSerializer(prescriptions, many=True)
            response_data = {
                'message_code': 1000,
                'message_text': 'Prescription details fetched successfully.',
                'message_data': serializer.data,
                'message_debug': debug
            }
        except Tblprescriptions.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Prescription details not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(["POST"])
def update_prescription_details(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_debug': debug
    }

    # Extract data from the request
    consultation_id = request.data.get('consultation_id', None)

    # Check if required data is provided
    if not consultation_id:
        response_data = {'message_code': 999, 'message_text': 'Consultation ID is required.'}
    else:
        try:
            # Retrieve the prescription instance based on consultation ID
            prescription = Tblprescriptions.objects.get(consultation_id=consultation_id)

            # Create a serializer instance with the instance and request data
            serializer = TblPrescriptionsSerializer(prescription, data=request.data)

            # Validate the serializer
            if serializer.is_valid():
                # Save the updated instance
                serializer.save()

                response_data = {
                    'message_code': 1000,
                    'message_text': 'Prescription details updated successfully.',
                    'message_debug': debug
                }
            else:
                response_data['message_text'] = 'Invalid data provided.'
                response_data['message_debug'] = serializer.errors
        except Tblprescriptions.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Prescription details not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_consultation_status(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    consultation_id = request.data.get('consultation_id', None)
    consultation_status = request.data.get('consultation_status', None)

    if not consultation_id:
        response_data = {'message_code': 999, 'message_text': 'Consultation ID is required.'}
    elif not consultation_status:
        response_data = {'message_code': 999, 'message_text': 'Consultation status is required.'}
    else:
        try:
            consultation = Tblconsultations.objects.get(consultation_id=consultation_id)
            consultation.consultation_status = consultation_status
            consultation.save()
            response_data = {
                'message_code': 1000,
                'message_text': 'Consultation status updated successfully.',
                'message_data': {'consultation_id': consultation_id, 'consultation_status': consultation_status},
                'message_debug': debug
            }
        except Tblconsultations.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Consultation not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(["POST"])
def update_consultation_details(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    consultation_id = request.data.get('consultation_id', None)

    if not consultation_id:
        response_data = {'message_code': 999, 'message_text': 'Consultation ID is required.'}
    else:
        try:
            consultation = Tblconsultations.objects.get(consultation_id=consultation_id)
            serializer = ConsultationSerializer(consultation, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'message_code': 1000,
                    'message_text': 'Consultation details updated successfully.',
                    'message_data': serializer.data,
                    'message_debug': debug
                }
            else:
                response_data = {'message_code': 999, 'message_text': 'Invalid data.', 'message_debug': serializer.errors}
        except Tblconsultations.DoesNotExist:
            response_data = {'message_code': 999, 'message_text': 'Consultation not found.', 'message_debug': debug}

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_patient_findings_and_symptoms(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Functional part is commented.',
        'message_data': [],
        'message_debug': debug
    }

    # Extract data from the request
    consultation_id = request.data.get('consultation_id', None)

    # Check if required data is provided
    if not consultation_id:
        response_data = {'message_code': 999, 'message_text': 'Consultation ID is required.'}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve the patient findings and symptoms instance based on consultation ID
        patient_findings_symptoms = TblpatientFindingsandsymtoms.objects.get(consultation_id=consultation_id)

        # Create a serializer instance with the instance and request data
        serializer = TblpatientFindingsandsymtomsSerializer(patient_findings_symptoms, data=request.data)

        # Validate the serializer
        if serializer.is_valid():
            # Save the updated instance
            serializer.save()

            response_data = {
                'message_code': 1000,
                'message_text': 'Patient findings and symptoms updated successfully.',
                'message_debug': debug
            }
        else:
            response_data['message_text'] = 'Invalid data provided.'
            response_data['message_debug'] = serializer.errors
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    except TblpatientFindingsandsymtoms.DoesNotExist:
        response_data = {'message_code': 999, 'message_text': 'Patient findings and symptoms not found.', 'message_debug': debug}
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    
    return Response(response_data, status=status.HTTP_200_OK)
# end

#############new api###################################
# @api_view(["POST"])
# def get_consultations_by_patient_id(request):
#     # Retrieve the patient ID from the request data
#     patient_id = request.data.get('patient_id', None)

#     # Check if patient ID is provided
#     if not patient_id:
#         return Response({'message_code': 999, 'message_text': 'Patient ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         # Query consultations for the given patient ID
#         consultations = Tblconsultations.objects.filter(patient_id=patient_id, isdeleted=0)
#         serializer = ConsultationSerializer(consultations, many=True)

#         # Prepare response data
#         response_data = {
#             'message_code': 1000,
#             'message_text': 'Consultation details fetched successfully.',
#             'message_data': serializer.data
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

#     except Tblconsultations.DoesNotExist:
#         # Handle case when no consultations are found for the given patient ID
#         return Response({'message_code': 999, 'message_text': 'Consultations not found for the specified patient ID.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
def get_consultations_by_patient_id(request):
    # Retrieve the patient ID from the request data
    patient_id = request.data.get('patient_id', None)

    # Check if patient ID is provided
    if not patient_id:
        return Response({'message_code': 999, 'message_text': 'Patient ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Query consultations for the given patient ID
        consultations = Tblconsultations.objects.filter(patient_id=patient_id, isdeleted=0)

        if not consultations.exists():
            # Handle case when no consultations are found for the given patient ID
            return Response({'message_code': 999, 'message_text': 'Consultations not found for the specified patient ID.'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize consultations data
        serializer = ConsultationSerializer(consultations, many=True)

        # Prepare response data for successful retrieval
        response_data = {
            'message_code': 1000,
            'message_text': 'Consultation details fetched successfully.',
            'message_data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle other exceptions that may occur during query or serialization
        return Response({'message_code': 999, 'message_text': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])
def get_consultations_by_patient_and_doctor_id(request):
    # Retrieve the patient ID and doctor ID from the request data
    patient_id = request.data.get('patient_id', None)
    doctor_id = request.data.get('doctor_id', None)

    # Check if patient ID and doctor ID are provided
    if not patient_id:
        return Response({'message_code': 999, 'message_text': 'Patient ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not doctor_id:
        return Response({'message_code': 999, 'message_text': 'Doctor ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Query consultations for the given patient ID and doctor ID
        consultations = Tblconsultations.objects.filter(patient_id=patient_id, doctor_id=doctor_id)

        if not consultations.exists():
            # Handle case when no consultations are found for the given patient ID and doctor ID
            return Response({'message_code': 999, 'message_text': 'Consultations not found for the specified patient ID and doctor ID.'}, status=status.HTTP_404_NOT_FOUND)

        # Serialize consultations data
        serializer = ConsultationSerializer(consultations, many=True)

        # Prepare response data for successful retrieval
        response_data = {
            'message_code': 1000,
            'message_text': 'Consultation details fetched successfully.',
            'message_data': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle other exceptions that may occur during query or serialization
        return Response({'message_code': 999, 'message_text': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



####################Pharmacy
import random
import string

@api_view(["POST"])
def insert_pharmacist(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        shop_name = request.data.get('shop_name')
        shop_owner_number = request.data.get('shop_owner_number')

        # Validate required fields
        if not shop_name:
            response_data['message_text'] = 'Shop name is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not shop_owner_number:
            response_data['message_text'] = 'Shop owner number is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Generate a random 32-character pharmacist_token
        pharmacist_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

        # Prepare data for serializer
        pharmacist_data = request.data.copy()
        pharmacist_data['pharmacist_token'] = pharmacist_token

        current_datetime = datetime.now()
        pharmacist_data['created_on']=int(current_datetime.timestamp())

        serializer = tblPharmacistSerializer(data=pharmacist_data)

        if serializer.is_valid():
            serializer.save()

            response_data['message_code'] = 1000
            response_data['message_text'] = 'Pharmacist details inserted successfully.'
            response_data['message_data'] = serializer.data
        else:
            response_data['message_text'] = 'Invalid data provided.'
            response_data['message_debug'] = serializer.errors

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def pharmacistLogin(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        username = request.data.get('username')
        password = request.data.get('password')

        # Validate required fields
        if not username:
            response_data['message_text'] = 'Username is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not password:
            response_data['message_text'] = 'Password is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Check if pharmacist exists with the provided username and password
        try:
            pharmacist = tblPharmacist.objects.get(pharmacist_username=username, pharmacist_password=password)
            serializer = tblPharmacistSerializer(pharmacist)
            response_data['message_code'] = 1000
            response_data['message_text'] = 'Login successful.'
            response_data['message_data'] = serializer.data
            
        except tblPharmacist.DoesNotExist:
            response_data['message_text'] = 'Invalid username or password.'

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_pharmacist_details_bytoken(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        pharmacist_token = request.data.get('pharmacist_token')

        # Validate required field
        if not pharmacist_token:
            response_data['message_text'] = 'Pharmacist token is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch the pharmacist details using .get() since pharmacist_token is unique
        try:
            pharmacist = tblPharmacist.objects.get(pharmacist_token=pharmacist_token)
        except tblPharmacist.DoesNotExist:
            response_data['message_text'] = 'Pharmacist not found.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Serialize the data, excluding sensitive fields
        data = tblPharmacistSerializer(pharmacist).data
        data.pop('pharmacist_username', None)
        data.pop('pharmacist_password', None)

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Pharmacist details retrieved successfully.'
        response_data['message_data'] = data

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(["POST"])
def insert_doctor_pharmacist_link(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        doctor_id = request.data.get('doctor_id')
        location_id = request.data.get('location_id')
        pharmacist_id = request.data.get('pharmacist_id')

        # Validate required fields
        if not doctor_id:
            response_data['message_text'] = 'Doctor ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not location_id:
            response_data['message_text'] = 'Location ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not pharmacist_id:
            response_data['message_text'] = 'Pharmacist ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Check if the combination of doctor_id, location_id, and pharmacist_id already exists
        existing_link = tblDoctorPharmacistlink.objects.filter(
            doctor_id=doctor_id, location_id=location_id, pharmacist_id=pharmacist_id, is_deleted=0
        ).first()

        if existing_link:
            response_data['message_code']=1001
            response_data['message_text'] = 'already Approved'
            return Response(response_data, status=status.HTTP_200_OK)

        # Prepare data for serializer
        link_data = request.data.copy()

        current_datetime = datetime.now()
        link_data['created_on'] = int(current_datetime.timestamp())

        serializer = tblDoctorPharmacistlinkSerializer(data=link_data)

        if serializer.is_valid():
            serializer.save()

            response_data['message_code'] = 1000
            response_data['message_text'] = 'Doctor-Pharmacist linked successfully.'
            response_data['message_data'] = serializer.data
        else:
            response_data['message_text'] = 'Invalid data provided.'
            response_data['message_debug'] = serializer.errors

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


# @api_view(["POST"])
# def get_doctor_pharmacist_bydoctorid(request):
#     debug = []
#     response_data = {
#         'message_code': 999,
#         'message_text': 'Error occurred.',
#         'message_data': [],
#         'message_debug': debug
#     }

#     try:
#         doctor_id = request.data.get('doctor_id')

#         # Validate required field
#         if not doctor_id:
#             response_data['message_text'] = 'Doctor ID is required.'
#             return Response(response_data, status=status.HTTP_200_OK)

#         # Fetch all records linked to the provided doctor_id
#         doctor_pharmacist_links = tblDoctorPharmacistlink.objects.filter(doctor_id=doctor_id, is_deleted=0).order_by('-doctorpharmacist_id')

#         if doctor_pharmacist_links.exists():
#             serializer = tblDoctorPharmacistlinkSerializer(doctor_pharmacist_links, many=True)
#             response_data['message_code'] = 1000
#             response_data['message_text'] = 'Doctor-Pharmacist list retrieved successfully.'
#             response_data['message_data'] = serializer.data
#         else:
#             response_data['message_text'] = 'No Doctor-Pharmacist found for the provided Doctor ID.'

#     except Exception as e:
#         response_data['message_text'] = str(e)
#         debug.append(str(e))

#     return Response(response_data, status=status.HTTP_200_OK)
@api_view(["POST"])
def get_doctor_pharmacist_bydoctorid(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        doctor_id = request.data.get('doctor_id')
        Status = request.data.get('Status')
        # Validate required field
        if not doctor_id:
            response_data['message_text'] = 'Doctor ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if Status is None:  
            # Fetch all records as status is not passed
            doctor_pharmacist_links = tblDoctorPharmacistlink.objects.filter(
                doctor_id=doctor_id, 
                is_deleted=0
            ).order_by('-doctorpharmacist_id')
        
        else: 
            # Fetch only active or deactive record depending on status value if status=0 means active and if status=1 then deactive
            doctor_pharmacist_links = tblDoctorPharmacistlink.objects.filter(
                doctor_id=doctor_id, 
                status=Status,
                is_deleted=0,
            ).order_by('-doctorpharmacist_id')


        if doctor_pharmacist_links.exists():
            response_data['message_code'] = 1000
            response_data['message_text'] = 'Doctor-Pharmacist list retrieved successfully.'
            if(Status is not None):
                if(Status==0):
                    response_data['message_text'] = 'Active Approval  list retrieved successfully.'
                else:
                    response_data['message_text'] = 'Inactive Approval  list retrieved successfully.'


            response_data['message_data'] = []

            for link in doctor_pharmacist_links:
                link_data = tblDoctorPharmacistlinkSerializer(link).data

                # Fetch pharmacist details based on pharmacist_id
                pharmacist = link.pharmacist_id
                if pharmacist:
                    pharmacist_data = tblPharmacistSerializer(pharmacist).data
                    link_data['pharmacist_details'] = pharmacist_data

                response_data['message_data'].append(link_data)

        else:
            response_data['message_text'] = 'No Doctor-Pharmacist found for the provided Doctor ID.'

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)



@api_view(["POST"])
def update_doctor_pharmacist_status(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        doctorpharmacist_id = request.data.get('doctorpharmacist_id')
        new_status = request.data.get('status')

        # Validate required fields
        if not doctorpharmacist_id:
            response_data['message_text'] = 'DoctorPharmacist ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if new_status is None:
            response_data['message_text'] = 'Status is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch the record to update the status using .get()
        try:
            doctor_pharmacist_link = tblDoctorPharmacistlink.objects.get(
                doctorpharmacist_id=doctorpharmacist_id,
                is_deleted=0
            )
        except tblDoctorPharmacistlink.DoesNotExist:
            response_data['message_text'] = 'Doctor-Pharmacist link not found.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Update the status field
        doctor_pharmacist_link.status = new_status
        doctor_pharmacist_link.save()

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Status updated successfully.'
        response_data['message_data'] = tblDoctorPharmacistlinkSerializer(doctor_pharmacist_link).data

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def insert_prescribe_pharmacist(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        # Extract required fields from request
        doctor_id = request.data.get('doctor_id')
        patient_id = request.data.get('patient_id')
        prescription_id = request.data.get('prescription_id')
        pharmacist_id = request.data.get('pharmacist_id')

        # Validate required fields
        if not doctor_id:
            response_data['message_text'] = 'Doctor ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not patient_id:
            response_data['message_text'] = 'Patient ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not prescription_id:
            response_data['message_text'] = 'Prescription ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if not pharmacist_id:
            response_data['message_text'] = 'Pharmacist ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Prepare data for serializer
        link_data = request.data.copy()

        current_datetime = datetime.now()
        link_data['created_on'] = int(current_datetime.timestamp())
       

        serializer = tblPrescribePharmacistSerializer(data=link_data)

        if serializer.is_valid():
            serializer.save()

            response_data['message_code'] = 1000
            response_data['message_text'] = 'Pharmacist prescribed successfully.'
            response_data['message_data'] = serializer.data
        else:
            response_data['message_text'] = 'Invalid data provided.'
            response_data['message_debug'] = serializer.errors

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def get_pharmacist_doctor_bypharmacistid(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        pharmacist_id = request.data.get('pharmacist_id')
        Status = request.data.get('Status')

        # Validate required field
        if not pharmacist_id:
            response_data['message_text'] = 'Pharmacist ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if Status is None:  
            # Fetch all records as status is not passed
            doctor_pharmacist_links = tblDoctorPharmacistlink.objects.filter(
                pharmacist_id=pharmacist_id,
                is_deleted=0
            ).order_by('-doctorpharmacist_id')
        
        else: 
            # Fetch only active or inactive records depending on status value
            doctor_pharmacist_links = tblDoctorPharmacistlink.objects.filter(
                pharmacist_id=pharmacist_id, 
                status=Status,
                is_deleted=0,
            ).order_by('-doctorpharmacist_id')

        if doctor_pharmacist_links.exists():
            response_data['message_code'] = 1000
            response_data['message_text'] = 'Pharmacist-Doctor list retrieved successfully.'
            
            if Status is not None:
                if Status == 0:
                    response_data['message_text'] = 'Active Approval list retrieved successfully.'
                else:
                    response_data['message_text'] = 'Inactive Approval list retrieved successfully.'

            response_data['message_data'] = []

            for link in doctor_pharmacist_links:
                link_data = tblDoctorPharmacistlinkSerializer(link).data

                # Fetch doctor details based on doctor_id
                doctor = link.doctor_id
                if doctor:
                    doctor_data = DoctorSerializer(doctor).data

                    # Exclude password and login_token
                    doctor_data.pop('password', None)
                    doctor_data.pop('doctor_login_token', None)

                    link_data['doctor_details'] = doctor_data

                response_data['message_data'].append(link_data)

        else:
            response_data['message_text'] = 'No Doctor-Pharmacist found for the provided Pharmacist ID.'

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)



from datetime import datetime, timedelta

# @api_view(["POST"])
# def get_patientdetails_by_doctor_pharmacist_id(request):
#     debug = []
#     response_data = {
#         'message_code': 999,
#         'message_text': 'Error occurred.',
#         'message_data': [],
#         'message_debug': debug
#     }

#     try:
#         doctor_id = request.data.get('doctor_id')
#         pharmacist_id = request.data.get('pharmacist_id')

#         # Validate required fields
#         if not doctor_id or not pharmacist_id:
#             response_data['message_text'] = 'Doctor ID and Pharmacist ID are required.'
#             return Response(response_data, status=status.HTTP_200_OK)

#         # Calculate the date range: current date to previous 3 days
#         current_date = datetime.now()
#         previous_date = current_date - timedelta(days=3)
#         current_timestamp = int(current_date.timestamp())
#         previous_timestamp = int(previous_date.timestamp())
#         print(current_date,previous_date)

#         # Fetch records from tblPrescribePharmacist within the date range
#         prescribed_pharmacists = tblPrescribePharmacist.objects.filter(
#             doctor_id=doctor_id,
#             pharmacist_id=pharmacist_id,
#             created_on__range=(previous_timestamp, current_timestamp),
#             is_deleted=0
#         ).order_by('-created_on')

#         if prescribed_pharmacists.exists():
#             response_data['message_code'] = 1000
#             response_data['message_text'] = 'Patient prescription details retrieved successfully.'
#             response_data['message_data'] = []

#             for prescribe in prescribed_pharmacists:
#                 prescribe_data = tblPrescribePharmacistSerializer(prescribe).data

#                 # Fetch patient details based on patient_id
#                 patient = prescribe.patient_id
#                 if patient:
#                     patient_data = TblpatientsSerializer(patient).data
#                     prescribe_data['patient_details'] = patient_data

#                 # Fetch consultation ID from prescription based on prescription_id
#                 prescription = prescribe.prescription_id
#                 if prescription:
#                     prescribe_data['consultation_id'] = prescription.consultation_id.consultation_id

#                 response_data['message_data'].append(prescribe_data)
#         else:
#             response_data['message_text'] = 'No prescription records found for the provided Doctor and Pharmacist IDs.'

#     except Exception as e:
#         response_data['message_text'] = str(e)
#         debug.append(str(e))

#     return Response(response_data, status=status.HTTP_200_OK)

from datetime import datetime, timedelta

@api_view(["POST"])
def get_patientdetails_by_doctor_pharmacist_id(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        doctor_id = request.data.get('doctor_id')
        pharmacist_id = request.data.get('pharmacist_id')

        # Validate required fields
        if not doctor_id or not pharmacist_id:
            response_data['message_text'] = 'Doctor ID and Pharmacist ID are required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Calculate the date range: start from 12:00 AM of the previous day to 11:59 PM of the current day
        current_date = datetime.now().replace(hour=23, minute=59, second=59)  # 11:59 PM of the current day
        previous_date = (current_date - timedelta(days=3)).replace(hour=0, minute=0, second=0)  # 12:00 AM of the previous 3 day
        
        # print(current_date, previous_date)

        # Convert to timestamp for filtering
        current_timestamp = int(current_date.timestamp())
        previous_timestamp = int(previous_date.timestamp())

        # Fetch records from tblPrescribePharmacist within the updated date range
        prescribed_pharmacists = tblPrescribePharmacist.objects.filter(
            doctor_id=doctor_id,
            pharmacist_id=pharmacist_id,
            created_on__range=(previous_timestamp, current_timestamp),
            is_deleted=0
        ).order_by('-created_on')

        if prescribed_pharmacists.exists():
            response_data['message_code'] = 1000
            response_data['message_text'] = 'Patient prescription details retrieved successfully.'
            response_data['message_data'] = []

            for prescribe in prescribed_pharmacists:
                prescribe_data = tblPrescribePharmacistSerializer(prescribe).data

                # Fetch patient details based on patient_id
                patient = prescribe.patient_id
                if patient:
                    patient_data = TblpatientsSerializer(patient).data
                    prescribe_data['patient_details'] = patient_data

                # Fetch consultation ID from prescription based on prescription_id
                prescription = prescribe.prescription_id
                if prescription:
                    prescribe_data['consultation_id'] = prescription.consultation_id.consultation_id

                response_data['message_data'].append(prescribe_data)
        else:
            response_data['message_text'] = 'No prescription records found for the provided Doctor and Pharmacist IDs.'

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def update_pharma_status(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        # Get the prescribepharmacist_id and pharma_status from the request
        prescribepharmacist_id = request.data.get('prescribepharmacist_id')
        pharma_status = request.data.get('pharma_status')

        # Validate required fields
        if not prescribepharmacist_id:
            response_data['message_text'] = 'Prescribe Pharmacist ID is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        if pharma_status is None:
            response_data['message_text'] = 'Pharma status is required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Fetch the record by prescribepharmacist_id
        try:
            prescribe_pharmacist_record = tblPrescribePharmacist.objects.get(
                prescribepharmacist_id=prescribepharmacist_id, 
                is_deleted=0
            )
        except tblPrescribePharmacist.DoesNotExist:
            response_data['message_text'] = 'Record not found.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Update the pharma_status
        prescribe_pharmacist_record.pharma_status = pharma_status
        prescribe_pharmacist_record.save()

        # Serialize the updated data
        serializer = tblPrescribePharmacistSerializer(prescribe_pharmacist_record)
        response_data['message_code'] = 1000
        response_data['message_text'] = 'Pharma status updated successfully.'
        response_data['message_data'] = serializer.data

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(["POST"])
def filter_patientdetails_by_options(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': [],
        'message_debug': debug
    }

    try:
        doctor_id = request.data.get('doctor_id')
        pharmacist_id = request.data.get('pharmacist_id')
        pharma_status = request.data.get('pharma_status')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        # Validate required fields
        if not doctor_id or not pharmacist_id:
            response_data['message_text'] = 'Doctor ID and Pharmacist ID are required.'
            return Response(response_data, status=status.HTTP_200_OK)

        # Initialize filter query
        filter_conditions = {
            'doctor_id': doctor_id,
            'pharmacist_id': pharmacist_id,
            'is_deleted': 0
        }

        # Filter by pharma_status if provided
        if pharma_status is not None:
            filter_conditions['pharma_status'] = pharma_status

        # Handle date filtering logic
        if start_date and end_date:
            # Filter by start and end date range
            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            epoch_start_date = int(start_date_dt.timestamp())
            epoch_end_date = int(end_date_dt.timestamp())
            filter_conditions['created_on__range'] = (epoch_start_date, epoch_end_date)
        elif start_date:
            # Filter by start date only (same day)
            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
            end_date_dt = start_date_dt.replace(hour=23, minute=59, second=59)
            epoch_start_date = int(start_date_dt.timestamp())
            epoch_end_date = int(end_date_dt.timestamp())
            filter_conditions['created_on__range'] = (epoch_start_date, epoch_end_date)

        print(filter_conditions)
        # Fetch records based on the filter conditions
        prescribed_pharmacists = tblPrescribePharmacist.objects.filter(
            **filter_conditions
        ).order_by('-created_on')

        if prescribed_pharmacists.exists():
            response_data['message_code'] = 1000
            response_data['message_text'] = 'Filtered prescription details retrieved successfully.'
            response_data['message_data'] = []

            for prescribe in prescribed_pharmacists:
                prescribe_data = tblPrescribePharmacistSerializer(prescribe).data

                # Fetch patient details based on patient_id
                patient = prescribe.patient_id
                if patient:
                    patient_data = TblpatientsSerializer(patient).data
                    prescribe_data['patient_details'] = patient_data

                # Fetch consultation ID from prescription based on prescription_id
                prescription = prescribe.prescription_id
                if prescription:
                    prescribe_data['consultation_id'] = prescription.consultation_id.consultation_id

                response_data['message_data'].append(prescribe_data)
        else:
            response_data['message_text'] = 'No prescription records found for the provided filter options.'

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=status.HTTP_200_OK)

from django.db.models import Count
@api_view(["POST"])
def get_pharmacist_stats(request):
    debug = []
    response_data = {
        'message_code': 999,
        'message_text': 'Error occurred.',
        'message_data': {},
        'message_debug': debug
    }

    try:
        pharmacist_id = request.data.get('pharmacist_id')

        # Validate required field
        if not pharmacist_id:
            response_data['message_text'] = 'Pharmacist ID is required.'
            return Response(response_data, status=200)

        # Total doctors associated with the pharmacist (status=0 for active)
        total_doctor_count = tblDoctorPharmacistlink.objects.filter(
            pharmacist_id=pharmacist_id,
            status=0,  # 0 means active or associated
            is_deleted=0
        ).count()

        # Count pharma_status for each status (0-5)
        pharma_status_counts = tblPrescribePharmacist.objects.filter(
            pharmacist_id=pharmacist_id,
            is_deleted=0
        ).values('pharma_status').annotate(count=Count('pharma_status'))

        # Unique patients associated with the pharmacist (distinct patient_ids)
        unique_patient_count = tblPrescribePharmacist.objects.filter(
            pharmacist_id=pharmacist_id,
            is_deleted=0
        ).values('patient_id').distinct().count()

        # Preparing the message data for response
        pharma_status_dict = {status['pharma_status']: status['count'] for status in pharma_status_counts}
        response_data['message_data'] = {
            'total_doctor_count': total_doctor_count,
            'pharma_status_counts': pharma_status_dict,
            'unique_patient_count': unique_patient_count
        }

        response_data['message_code'] = 1000
        response_data['message_text'] = 'Pharmacist counts retrieved successfully.'

    except Exception as e:
        response_data['message_text'] = str(e)
        debug.append(str(e))

    return Response(response_data, status=200)




