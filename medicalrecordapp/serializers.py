# from rest_framework import serializers
# from .models import *



# class PatientBiometricsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tblpatientbiometrics
#         fields = '__all__'

# class ConsultationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tblconsultations
#         fields = '__all__'

# class PrescriptionsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tblprescriptions
#         fields = '__all__'


# class FindingsandsymtomsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblpatientFindingsandsymtoms
#         fields = '__all__'

# class MedicationsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblpatientMedications
#         fields = '__all__'

# class LabinvestigationsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblpatientLabinvestigations
#         fields = '__all__'

# ######################### Patient Vitals ############################   
# class TblPatientVitalsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tblpatientvitals
#         fields = '__all__'

# ######################### Patient Findingsandsymtoms ############################   
# class TblpatientFindingsandsymtomsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblpatientFindingsandsymtoms
#         fields = [
#             'patient_id',
#             'doctor_id',
#             'patient_status',
#             'findgings_datetime',
#             'consultation_id',
#             'findings',
#             'symtoms',
#             'isdeleted',
#         ]

# ######################### Patient Complaints ############################   
# class TblpatientComplaintsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TblpatientComplaints
#         fields = [
#             'doctor_id',
#             'patient_id',
#             'complaint_datetime',
#             'complaint_details',
#             'appointment_id',
#             'consultation_id',
#             'isdeleted',
#         ]

