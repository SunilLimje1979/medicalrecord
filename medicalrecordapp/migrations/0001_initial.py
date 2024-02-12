# Generated by Django 5.0.2 on 2024-02-11 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
            ],
            options={
                'db_table': 'auth_group',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('codename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'auth_permission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.IntegerField()),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.CharField(max_length=254)),
                ('is_staff', models.IntegerField()),
                ('is_active', models.IntegerField()),
                ('date_joined', models.DateTimeField()),
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserUserPermissions',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'auth_user_user_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoAdminLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_time', models.DateTimeField()),
                ('object_id', models.TextField(blank=True, null=True)),
                ('object_repr', models.CharField(max_length=200)),
                ('action_flag', models.PositiveSmallIntegerField()),
                ('change_message', models.TextField()),
            ],
            options={
                'db_table': 'django_admin_log',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoContentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('app_label', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'django_content_type',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoMigrations',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('app', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('applied', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_migrations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
                ('session_key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('session_data', models.TextField()),
                ('expire_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_session',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tblconsultations',
            fields=[
                ('consultation_id', models.AutoField(db_column='Consultation_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('patient_status', models.SmallIntegerField(db_column='Patient_Status')),
                ('consultation_datetime', models.IntegerField(db_column='Consultation_DateTime')),
                ('consultation_mode', models.SmallIntegerField(db_column='Consultation_Mode')),
                ('visit_reason', models.CharField(blank=True, db_column='Visit_Reason', max_length=255, null=True)),
                ('consultation_duration', models.IntegerField(blank=True, db_column='Consultation_Duration', null=True)),
                ('further_assited', models.IntegerField(db_column='Further_Assited')),
                ('followup_datetime', models.IntegerField(blank=True, db_column='Followup_DateTime', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deleted_reason', models.CharField(blank=True, db_column='Deleted_Reason', max_length=100, null=True)),
            ],
            options={
                'db_table': 'tblconsultations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tbldatacodemaster',
            fields=[
                ('datacodeid', models.AutoField(db_column='DataCodeId', primary_key=True, serialize=False)),
                ('datacodename', models.CharField(db_column='DataCodeName', max_length=20)),
                ('datacodevalue', models.CharField(db_column='DataCodeValue', max_length=5)),
                ('datacodedescription', models.TextField(db_column='DataCodeDescription')),
            ],
            options={
                'db_table': 'tbldatacodemaster',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tbldoctorappointments',
            fields=[
                ('appointment_id', models.AutoField(db_column='Appointment_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('appointment_datetime', models.BigIntegerField(db_column='Appointment_DateTime')),
                ('appointment_token', models.IntegerField(db_column='Appointment_Token')),
                ('appointment_name', models.CharField(db_column='Appointment_Name', max_length=100)),
                ('appointment_mobileno', models.CharField(db_column='Appointment_MobileNo', max_length=10)),
                ('appointment_gender', models.IntegerField(db_column='Appointment_Gender')),
                ('appointment_status', models.IntegerField(db_column='Appointment_Status')),
                ('consultation_id', models.IntegerField(blank=True, db_column='Consultation_Id', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
            ],
            options={
                'db_table': 'tbldoctorappointments',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tbldoctorlocationavailability',
            fields=[
                ('doctor_location_availability_id', models.AutoField(db_column='Doctor_Location_Availability_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('doctor_location_id', models.IntegerField(db_column='Doctor_Location_Id')),
                ('availability_day', models.SmallIntegerField(db_column='Availability_Day')),
                ('availability_starttime', models.CharField(db_column='Availability_StartTime', max_length=8)),
                ('availability_endtime', models.IntegerField(db_column='Availability_EndTime')),
                ('availability_status', models.IntegerField(db_column='Availability_Status')),
                ('availability_order', models.IntegerField(db_column='Availability_Order')),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deletedreason', models.IntegerField(blank=True, db_column='DeletedReason', null=True)),
            ],
            options={
                'db_table': 'tbldoctorlocationavailability',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tbldoctorlocations',
            fields=[
                ('doctor_location_id', models.AutoField(db_column='Doctor_Location_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('location_title', models.CharField(db_column='Location_Title', max_length=100)),
                ('location_type', models.IntegerField(db_column='Location_Type')),
                ('location_address', models.CharField(db_column='Location_Address', max_length=255)),
                ('location_latitute', models.CharField(blank=True, db_column='Location_Latitute', max_length=15, null=True)),
                ('location_longitute', models.CharField(blank=True, db_column='Location_Longitute', max_length=15, null=True)),
                ('location_city_id', models.IntegerField(db_column='Location_City_Id')),
                ('location_state_id', models.IntegerField(db_column='Location_State_Id')),
                ('location_country_id', models.IntegerField(db_column='Location_Country_Id')),
                ('location_pincode', models.CharField(db_column='Location_Pincode', max_length=6)),
                ('location_status', models.IntegerField(db_column='Location_Status')),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deletedreason', models.CharField(blank=True, db_column='DeletedReason', max_length=200, null=True)),
            ],
            options={
                'db_table': 'tbldoctorlocations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TbldoctorMedicines',
            fields=[
                ('doctor_medicine_id', models.AutoField(db_column='Doctor_Medicine_Id', primary_key=True, serialize=False)),
                ('medicine_code', models.CharField(db_column='Medicine_Code', max_length=5)),
                ('medicine_name', models.CharField(db_column='Medicine_Name', max_length=100)),
                ('medicine_form', models.SmallIntegerField(db_column='Medicine_Form')),
                ('medicine_frequency', models.CharField(db_column='Medicine_Frequency', max_length=3)),
                ('medicine_duration', models.IntegerField(db_column='Medicine_Duration')),
                ('medicine_dosages', models.IntegerField(db_column='Medicine_Dosages')),
                ('medicine_manufacture', models.CharField(db_column='Medicine_Manufacture', max_length=100)),
                ('medicine_packsize', models.IntegerField(db_column='Medicine_PackSize')),
                ('medicine_preservation', models.IntegerField(db_column='Medicine_Preservation')),
                ('medicine_minstock', models.IntegerField(db_column='Medicine_MinStock')),
                ('medicine_gst', models.IntegerField(db_column='Medicine_GST')),
                ('medicine_content_name', models.CharField(db_column='Medicine_Content_Name', max_length=100)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deletedreason', models.CharField(blank=True, db_column='DeletedReason', max_length=100, null=True)),
            ],
            options={
                'db_table': 'tbldoctor_medicines',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tbldoctors',
            fields=[
                ('doctor_id', models.AutoField(db_column='Doctor_Id', primary_key=True, serialize=False)),
                ('doctor_firstname', models.CharField(db_column='Doctor_Firstname', max_length=50)),
                ('doctor_lastname', models.CharField(db_column='Doctor_Lastname', max_length=50)),
                ('doctor_mobileno', models.CharField(db_column='Doctor_MobileNo', max_length=10)),
                ('doctor_email', models.CharField(db_column='Doctor_Email', max_length=100)),
                ('doctor_dateofbirth', models.IntegerField(blank=True, db_column='Doctor_DateofBirth', null=True)),
                ('doctor_maritalstatus', models.IntegerField(db_column='Doctor_MaritalStatus')),
                ('doctor_gender', models.SmallIntegerField(db_column='Doctor_Gender')),
                ('doctor_aadharnumber', models.CharField(db_column='Doctor_AadharNumber', max_length=16)),
                ('doctor_address', models.CharField(blank=True, db_column='Doctor_Address', max_length=1000, null=True)),
                ('doctor_cityid', models.IntegerField(blank=True, db_column='Doctor_CityId', null=True)),
                ('doctor_stateid', models.IntegerField(blank=True, db_column='Doctor_StateId', null=True)),
                ('doctor_countryid', models.IntegerField(blank=True, db_column='Doctor_CountryId', null=True)),
                ('doctor_pincode', models.CharField(blank=True, db_column='Doctor_Pincode', max_length=6, null=True)),
                ('doctor_registrationno', models.CharField(db_column='Doctor_RegistrationNo', max_length=50)),
                ('doctor_profilleimageurl', models.IntegerField(blank=True, db_column='Doctor_ProfilleImageURL', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('isactive', models.IntegerField(db_column='IsActive')),
            ],
            options={
                'db_table': 'tbldoctors',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TblmedicineInstructions',
            fields=[
                ('doctor_instruction_id', models.AutoField(db_column='Doctor_Instruction_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('instruction_language', models.CharField(db_column='Instruction_Language', max_length=2)),
                ('instruction_text', models.CharField(db_collation='utf8mb4_unicode_ci', db_column='Instruction_Text', max_length=100)),
            ],
            options={
                'db_table': 'tblmedicine_instructions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TblpateintCharges',
            fields=[
                ('pateint_charges_id', models.AutoField(db_column='Pateint_Charges_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('patient_status', models.IntegerField(db_column='Patient_Status')),
                ('charges_referencetype', models.IntegerField(db_column='Charges_ReferenceType')),
                ('charges_reference_id', models.IntegerField(db_column='Charges_Reference_Id')),
                ('charges_type', models.IntegerField(db_column='Charges_Type')),
                ('charges_category', models.IntegerField(db_column='Charges_Category')),
                ('charges_notes', models.CharField(blank=True, db_column='Charges_Notes', max_length=100, null=True)),
                ('charges_units', models.IntegerField(db_column='Charges_Units')),
                ('charges_rate', models.IntegerField(db_column='Charges_Rate')),
                ('charges_amount', models.IntegerField(db_column='Charges_Amount')),
                ('charges_discount', models.IntegerField(blank=True, db_column='Charges_Discount', null=True)),
                ('charges_discount_reason', models.IntegerField(blank=True, db_column='Charges_Discount_Reason', null=True)),
                ('charges_discountby', models.CharField(blank=True, db_column='Charges_DiscountBy', max_length=50, null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deleted_reason', models.IntegerField(blank=True, db_column='Deleted_Reason', null=True)),
            ],
            options={
                'db_table': 'tblpateint_charges',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tblpatientbiometrics',
            fields=[
                ('patient_biometricid', models.AutoField(db_column='Patient_Biometricid', primary_key=True, serialize=False)),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('consultation_id', models.IntegerField(blank=True, db_column='Consultation_Id', null=True)),
                ('operator_id', models.IntegerField(blank=True, db_column='Operator_Id', null=True)),
                ('patient_status', models.IntegerField(db_column='Patient_Status')),
                ('patient_height', models.FloatField(blank=True, db_column='Patient_Height', null=True)),
                ('patient_weight', models.FloatField(blank=True, db_column='Patient_Weight', null=True)),
                ('patient_bmi', models.FloatField(blank=True, db_column='Patient_BMI', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
            ],
            options={
                'db_table': 'tblpatientbiometrics',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TblpatientComplaints',
            fields=[
                ('patient_complaint_id', models.AutoField(db_column='Patient_Complaint_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('complaint_datetime', models.IntegerField(db_column='Complaint_DateTime')),
                ('complaint_details', models.TextField(db_column='Complaint_Details')),
                ('appointment_id', models.IntegerField(blank=True, db_column='Appointment_Id', null=True)),
                ('consultation_id', models.IntegerField(blank=True, db_column='Consultation_Id', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deleted_reason', models.IntegerField(blank=True, db_column='Deleted_Reason', null=True)),
            ],
            options={
                'db_table': 'tblpatient_complaints',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TblpatientFindingsandsymtoms',
            fields=[
                ('patient_findings_id', models.AutoField(db_column='Patient_Findings_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('patient_status', models.SmallIntegerField(db_column='Patient_Status')),
                ('findgings_datetime', models.IntegerField(db_column='Findgings_DateTime')),
                ('consultation_id', models.IntegerField(blank=True, db_column='Consultation_Id', null=True)),
                ('findings', models.TextField(db_column='Findings')),
                ('symtoms', models.TextField(db_column='Symtoms')),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deleted_reason', models.CharField(db_column='Deleted_Reason', max_length=100)),
            ],
            options={
                'db_table': 'tblpatient_findingsandsymtoms',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TblpatientLabinvestigations',
            fields=[
                ('patient_labinvestigation_id', models.AutoField(db_column='Patient_LabInvestigation_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('patient_status', models.IntegerField(db_column='Patient_Status')),
                ('consultation_id', models.IntegerField(db_column='Consultation_Id')),
                ('prescription_id', models.IntegerField(db_column='Prescription_Id')),
                ('labinvestigation_datetime', models.IntegerField(db_column='LabInvestigation_DateTime')),
                ('labinvestigation_category', models.IntegerField(db_column='LabInvestigation_Category')),
                ('patient_labtestid', models.IntegerField(db_column='Patient_LabTestId')),
                ('patient_labtestreport', models.CharField(db_column='Patient_LabTestReport', max_length=100)),
                ('patient_labtestsample', models.IntegerField(db_column='Patient_LabTestSample')),
                ('patient_labtestreport_check', models.IntegerField(db_column='Patient_LabTestReport_Check')),
                ('lattest_extrafield1', models.IntegerField(blank=True, db_column='LatTest_ExtraField1', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('deletedon', models.IntegerField(blank=True, db_column='DeletedOn', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deleted_reason', models.CharField(blank=True, db_column='Deleted_Reason', max_length=100, null=True)),
                ('isdeleted', models.IntegerField(db_column='IsDeleted')),
            ],
            options={
                'db_table': 'tblpatient_labinvestigations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TblpatientMedications',
            fields=[
                ('patient_medication_id', models.AutoField(db_column='Patient_Medication_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('patient_status', models.IntegerField(db_column='Patient_Status')),
                ('consultation_id', models.IntegerField(db_column='Consultation_Id')),
                ('prescription_id', models.IntegerField(db_column='Prescription_Id')),
                ('medication_datetime', models.IntegerField(db_column='Medication_DateTime')),
                ('medicine_id', models.IntegerField(db_column='Medicine_Id')),
                ('medicine_form', models.CharField(db_column='Medicine_Form', max_length=5)),
                ('medicine_name', models.CharField(db_column='Medicine_Name', max_length=100)),
                ('medicine_duration', models.IntegerField(db_column='Medicine_Duration')),
                ('medicine_doses', models.IntegerField(db_column='Medicine_Doses')),
                ('medicine_dose_interval', models.CharField(db_column='Medicine_Dose_Interval', max_length=15)),
                ('medicine_instruction_id', models.IntegerField(blank=True, db_column='Medicine_Instruction_Id', null=True)),
                ('medicine_category', models.IntegerField(blank=True, db_column='Medicine_Category', null=True)),
                ('medicine_extrafield1', models.IntegerField(blank=True, db_column='Medicine_ExtraField1', null=True)),
                ('medicine_extrafield2', models.IntegerField(blank=True, db_column='Medicine__ExtraField2', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deleted_reason', models.CharField(blank=True, db_column='Deleted_Reason', max_length=100, null=True)),
            ],
            options={
                'db_table': 'tblpatient_medications',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TblpatientPayments',
            fields=[
                ('patient_payment_id', models.AutoField(db_column='Patient_Payment_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('patient_status', models.IntegerField(db_column='Patient_Status')),
                ('payment_mode', models.IntegerField(db_column='Payment_Mode')),
                ('payment_amount', models.IntegerField(db_column='Payment_Amount')),
                ('payment_transaction_no', models.CharField(blank=True, db_column='Payment_Transaction_No', max_length=100, null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deleted_reason', models.IntegerField(blank=True, db_column='Deleted_Reason', null=True)),
            ],
            options={
                'db_table': 'tblpatient_payments',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tblpatients',
            fields=[
                ('patient_id', models.AutoField(db_column='Patient_Id', primary_key=True, serialize=False)),
                ('patient_mobileno', models.CharField(db_column='Patient_MobileNo', max_length=10)),
                ('patient_firstname', models.CharField(db_column='Patient_Firstname', max_length=50)),
                ('patient_fateherhusbandname', models.CharField(blank=True, db_column='Patient_FateherHusbandName', max_length=50, null=True)),
                ('patient_lastname', models.CharField(db_column='Patient_Lastname', max_length=50)),
                ('patient_gender', models.SmallIntegerField(db_column='Patient_Gender')),
                ('patient_dateofbirth', models.BigIntegerField(blank=True, db_column='Patient_DateOfBirth', null=True)),
                ('patient_maritalstatus', models.IntegerField(db_column='Patient_MaritalStatus')),
                ('patient_aadharnumber', models.CharField(blank=True, db_column='Patient_AadharNumber', max_length=16, null=True)),
                ('patient_universalhealthid', models.IntegerField(db_column='Patient_UniversalHealthId')),
                ('patient_bloodgroup', models.IntegerField(db_column='Patient_BloodGroup')),
                ('patient_level', models.CharField(db_column='Patient_Level', max_length=1)),
                ('patient_emergencycontact', models.CharField(db_column='Patient_EmergencyContact', max_length=10)),
                ('patient_address', models.CharField(blank=True, db_column='Patient_Address', max_length=100, null=True)),
                ('patient_cityid', models.IntegerField(blank=True, db_column='Patient_CityId', null=True)),
                ('patient_stateid', models.IntegerField(blank=True, db_column='Patient_StateId', null=True)),
                ('patient_countryid', models.IntegerField(db_column='Patient_CountryId')),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('createdon', models.BigIntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('istestpatient', models.IntegerField(db_column='IsTestPatient')),
            ],
            options={
                'db_table': 'tblpatients',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tblpatientvitals',
            fields=[
                ('patient_biometricid', models.AutoField(db_column='Patient_Biometricid', primary_key=True, serialize=False)),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('consultation_id', models.IntegerField(blank=True, db_column='Consultation_Id', null=True)),
                ('operator_id', models.IntegerField(blank=True, db_column='Operator_Id', null=True)),
                ('patient_status', models.IntegerField(db_column='Patient_Status')),
                ('patient_heartratepluse', models.FloatField(db_column='Patient_HeartRatePluse')),
                ('patient_bpsystolic', models.FloatField(db_column='Patient_BPSystolic')),
                ('patient_bpdistolic', models.FloatField(db_column='Patient_BPDistolic')),
                ('patient_painscale', models.FloatField(db_column='Patient_PainScale')),
                ('patient_respiratoryrate', models.FloatField(db_column='Patient_RespiratoryRate')),
                ('patient_temparature', models.FloatField(db_column='Patient_Temparature')),
                ('patient_chest', models.CharField(db_column='Patient_Chest', max_length=100)),
                ('patient_ecg', models.CharField(db_column='Patient_ECG', max_length=100)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
            ],
            options={
                'db_table': 'tblpatientvitals',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tblprescriptions',
            fields=[
                ('prescriptions_id', models.AutoField(db_column='Prescriptions_Id', primary_key=True, serialize=False)),
                ('doctor_id', models.IntegerField(db_column='Doctor_Id')),
                ('patient_id', models.IntegerField(db_column='Patient_Id')),
                ('patient_status', models.IntegerField(db_column='Patient_Status')),
                ('consultation_id', models.IntegerField(db_column='Consultation_Id')),
                ('prescription_datetime', models.IntegerField(db_column='Prescription_DateTime')),
                ('prescription_details', models.TextField(blank=True, db_column='Prescription_Details', null=True)),
                ('createdon', models.IntegerField(blank=True, db_column='CreatedOn', null=True)),
                ('createdby', models.IntegerField(blank=True, db_column='CreatedBy', null=True)),
                ('lastmodifiedon', models.IntegerField(blank=True, db_column='LastModifiedOn', null=True)),
                ('lastmodifiedby', models.IntegerField(blank=True, db_column='LastModifiedBy', null=True)),
                ('isdeleted', models.IntegerField(blank=True, db_column='IsDeleted', null=True)),
                ('deletedby', models.IntegerField(blank=True, db_column='DeletedBy', null=True)),
                ('deleted_reason', models.IntegerField(blank=True, db_column='Deleted_Reason', null=True)),
            ],
            options={
                'db_table': 'tblprescriptions',
                'managed': False,
            },
        ),
    ]
